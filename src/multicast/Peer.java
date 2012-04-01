package multicast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.StringTokenizer;

import multicast.search.ParameterSearchImpl;
import multicast.search.message.SearchMessage.SearchType;
import multicast.search.message.SearchResponseMessage;
import peer.message.MessageID;
import peer.message.MessageStringPayload;
import peer.message.PayloadMessage;
import peer.peerid.PeerID;
import peer.peerid.PeerIDSet;
import taxonomy.parameter.InvalidParameterIDException;
import taxonomy.parameter.Parameter;
import taxonomy.parameter.ParameterFactory;
import taxonomy.parameterList.ParameterList;
import util.logger.Logger;
import util.timer.Timer;
import util.timer.TimerTask;

import common.CommonAgentJ;

import config.Configuration;
import dissemination.DistanceChange;
import dissemination.TableChangedListener;

/**
 * This is an implementation of a peer which uses and tests the parameter
 * multicast layer. It is intended for testing purposes.
 * 
 * @author Unai Aguilera (unai.aguilera@gmail.com)
 * 
 */
public class Peer extends CommonAgentJ implements ParameterSearchListener, TableChangedListener, TimerTask {

	private static final String REMOVE_PARAMETER = "removeParameter";

	private static final String ADD_PARAMETER = "addParameter";

	private static final String CANCEL_SEARCH = "cancelSearch";

	private static final String SEARCH_PARAMETER = "searchParameter";

	private static final String SEARCH_PARAMETER_GENERIC = "searchParameterGeneric";

	private static final String PARAMETERS_DIR = "parameters";

	private static final String GENERALIZE_SEARCH = "generalizeSearch";

	private final ParameterSearch pSearch;

	private final Logger myLogger = Logger.getLogger(Peer.class);
	
	private Timer unicastTimer = null;
	
	private boolean searchesPerformed = false;
	private float startTime, endTime;

	public Peer() {
		pSearch = new ParameterSearchImpl(peer, this, this);
	}

	@Override
	protected boolean peerCommands(final String command, final String[] args) {
		if (command.equals(SEARCH_PARAMETER)) {
			if (args.length > 0)
				try {
					final Set<Parameter> searchedParameters = parseParameters(args);
					pSearch.sendSearchMessageDefaultTTL(searchedParameters, new MessageStringPayload(peer.getPeerID(), "Hello, parameter"), SearchType.Exact);
					searchesPerformed = true;
					return true;
				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
					return false;
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + SEARCH_PARAMETER + " had no arguments");
		} else if (command.equals(SEARCH_PARAMETER_GENERIC)) {
			if (args.length > 0)
				try {
					final Set<Parameter> searchedParameters = parseParameters(args);
					pSearch.sendSearchMessageDefaultTTL(searchedParameters, new MessageStringPayload(peer.getPeerID(), "Hello, parameter"), SearchType.Generic);
					searchesPerformed = true;
					return true;
				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
					return false;
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + SEARCH_PARAMETER + " had no arguments");
		} else if (command.equals(CANCEL_SEARCH)) {
			if (args.length > 0)
				try {
					final Set<Parameter> canceledParameters = parseParameters(args);
					pSearch.sendCancelSearchMessage(canceledParameters);
					return true;
				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
					return false;
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + CANCEL_SEARCH + " had no arguments");
		} else if (command.equals(ADD_PARAMETER)) {
			if (args.length > 0)
				try {
					final Set<Parameter> addedParameters = parseParameters(args);
					for (final Parameter parameter : addedParameters) {
						myLogger.info("Peer " + peer.getPeerID() + " adding local parameter: " + parameter);
						pSearch.addLocalParameter(parameter);
					}

					myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
					pSearch.commit();

					return true;
				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
					return false;
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + ADD_PARAMETER + " had no arguments");
		} else if (command.equals(REMOVE_PARAMETER)) {
			if (args.length > 0)
				try {
					final Set<Parameter> removedParameters = parseParameters(args);
					for (final Parameter parameter : removedParameters) {
						myLogger.info("Peer " + peer.getPeerID() + " removing local parameter: " + parameter);
						pSearch.removeLocalParameter(parameter);
					}

					myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
					pSearch.commit();

					return true;
				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
					return false;
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + REMOVE_PARAMETER + " had no arguments");
		} else if (command.equals(GENERALIZE_SEARCH) && args.length > 0)
			try {
				final Set<Parameter> generalizedParameters = parseParameters(args);
				pSearch.sendGeneralizeSearchMessage(generalizedParameters);
				return true;
			} catch (final InvalidParameterIDException ipe) {
				myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
				return false;
			}
		return false;
	}

	private Set<Parameter> parseParameters(final String[] args) throws InvalidParameterIDException {
		final Set<Parameter> removedParameters = new HashSet<Parameter>();
		for (final String arg : args)
			removedParameters.add(ParameterFactory.createParameter(arg, pSearch.getDisseminationLayer().getTaxonomy()));
		return removedParameters;
	}

	@Override
	public void loadData() {
		try {
			final String xmlPath = getParametersFilePath(peer.getPeerID());
			final ParameterList pList = new ParameterList(xmlPath, pSearch.getDisseminationLayer().getTaxonomy());

			for (final Parameter parameter : pList.getParameterSet()) {
				myLogger.info("Peer " + peer.getPeerID() + " adding local parameter: " + parameter);
				pSearch.addLocalParameter(parameter);
			}

			myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
			pSearch.commit();

		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " error loading data." + e.getMessage());
		}
		
		boolean unicastSearch = false;
		float unicastSearchFreq = 0.0f;
		
		try {
			// Configure internal properties
			final String searchFreqStr = Configuration.getInstance().getProperty("multicast.searchFreq");
			unicastSearchFreq = Float.parseFloat(searchFreqStr);
			myLogger.info("Peer " + peer.getPeerID() + " set UNICAST_SEARCH_FREQ " + unicastSearchFreq);
			unicastSearch = true;
		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " had problem loading configuration: " + e.getMessage());
		}
		
		try {
			// Configure internal properties
			final String timeRange = Configuration.getInstance().getProperty("timeRange");			
			final String discardTime = Configuration.getInstance().getProperty("discardTime");
			final String trimmed = timeRange.substring(1, timeRange.length() - 1);
			StringTokenizer tokenizer = new StringTokenizer(trimmed, ", ");
			
			final String startStr = tokenizer.nextToken();
			if (startStr.equals("'START'"))
				startTime = Float.parseFloat(discardTime);
			else
				startTime = Float.parseFloat(startStr);
			
			endTime = Float.parseFloat(tokenizer.nextToken());
			
			myLogger.info("Peer " + peer.getPeerID() + " set TIME_RANGE (" + startTime + ", " + endTime + ")");
		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " had problem loading configuration: " + e.getMessage());
		}
		
		if (unicastSearch) {
			final int unicastPeriod = Math.round(1.0f / unicastSearchFreq) * 1000;
			myLogger.info("Peer " + peer.getPeerID() + " unicast timer started with a period of " + unicastPeriod + " s");
			unicastTimer = new Timer(unicastPeriod, this);
			unicastTimer.start();
		}
	}

	private String getParametersFilePath(final PeerID peerID) {
		return PARAMETERS_DIR + File.separator + "Parameters" + peerID + ".xml";
	}

	private void printMulticastTable() {
		final String xmlPath = getUTableFilePath(peer.getPeerID());
		try {
			final FileOutputStream f = new FileOutputStream(xmlPath);
			pSearch.saveToXML(f);
			f.close();
		} catch (final IOException ioe) {
			myLogger.error("Peer " + peer.getPeerID() + " error writting output data." + ioe.getMessage());
		}
		
		if (unicastTimer != null)
			unicastTimer.stopAndWait();
	}

	private String getUTableFilePath(final PeerID peerID) {
		return TEMP_DIR + File.separator + "UTable" + peerID + ".xml";
	}

	@Override
	public void printOutputs() {
		printMulticastTable();
	}

	@Override
	public void parametersFound(final SearchResponseMessage receivedMessage) {}

	@Override
	public PayloadMessage searchReceived(final Set<Parameter> foundParameters, final MessageID routeID) {
		return null;
	}

	@Override
	public void searchCanceled(Set<MessageID> canceledSearches) {
				
	}

	@Override
	public void multicastMessageAccepted(final PeerID source, final PayloadMessage payload, final int distance) {}

	@Override
	public PayloadMessage parametersChanged(final PeerID neighbor, final Set<Parameter> newParameters, final Set<Parameter> removedParameters, final Set<Parameter> removedLocalParameters, final Map<Parameter, DistanceChange> changedParameters, Set<Parameter> addedParameters, final List<PayloadMessage> payloadMessages) {
		return null;
	}
	
	@Override
	public void lostDestinations(Set<PeerID> lostDestinations) {}

	@Override
	public void perform() throws InterruptedException {
		if (searchesPerformed && myLogger.getCurrentTimeSeconds() >= startTime && myLogger.getCurrentTimeSeconds() <= endTime) { 
			final List<PeerID> availableDestinations = new ArrayList<PeerID>(pSearch.getKnownDestinations());
			if (!availableDestinations.isEmpty())
				pSearch.sendMulticastMessage(new PeerIDSet(availableDestinations), new MessageStringPayload(peer.getPeerID(), "Hello, peers"));
		}
	}
}
