package multicast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import multicast.search.ParameterSearchImpl;
import multicast.search.message.SearchMessage;
import multicast.search.message.SearchMessage.SearchType;
import multicast.search.message.SearchResponseMessage;

import util.logger.Logger;

import peer.message.MessageID;
import peer.message.MessageString;
import peer.message.MessageStringPayload;
import peer.message.PayloadMessage;
import peer.peerid.PeerID;
import peer.peerid.PeerIDSet;
import taxonomy.parameter.InvalidParameterIDException;
import taxonomy.parameter.Parameter;
import taxonomy.parameter.ParameterFactory;
import taxonomy.parameterList.ParameterList;

import common.CommonAgentJ;

import dissemination.DistanceChange;
import dissemination.TableChangedListener;

/**
 * This is an implementation of a peer which uses and tests the parameter
 * multicast layer. It is intended for testing purposes.
 * 
 * @author Unai Aguilera (unai.aguilera@gmail.com)
 * 
 */
public class Peer extends CommonAgentJ implements ParameterSearchListener, TableChangedListener {

	private static final String REMOVE_PARAMETER = "removeParameter";

	private static final String ADD_PARAMETER = "addParameter";

	private static final String CANCEL_SEARCH = "cancelSearch";

	private static final String SEARCH_PARAMETER = "searchParameter";

	private static final String SEARCH_PARAMETER_GENERIC = "searchParameterGeneric";

	private static final String PARAMETERS_DIR = "parameters";

	private static final String GENERALIZE_SEARCH = "generalizeSearch";

	private final ParameterSearch pSearch;

	private final PeerIDSet foundPeers = new PeerIDSet();

	private final Logger myLogger = Logger.getLogger(Peer.class);

	public Peer() {
		pSearch = new ParameterSearchImpl(peer, this, this);
	}

	@Override
	protected boolean peerCommands(final String command, final String[] args) {
		if (command.equals(SEARCH_PARAMETER)) {
			if (args.length > 0)
				try {
					final Set<Parameter> searchedParameters = parseParameters(args);
					pSearch.sendSearchMessage(searchedParameters, new MessageStringPayload(peer.getPeerID(), "Hello, parameter"), SearchType.Exact);
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
					pSearch.sendSearchMessage(searchedParameters, new MessageStringPayload(peer.getPeerID(), "Hello, parameter"), SearchType.Generic);
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
			removedParameters.add(ParameterFactory.createParameter(arg));
		return removedParameters;
	}

	@Override
	public void loadData() {
		try {
			final String xmlPath = getParametersFilePath(peer.getPeerID());
			final ParameterList pList = new ParameterList(xmlPath);

			for (final Parameter parameter : pList.getParameterSet()) {
				myLogger.info("Peer " + peer.getPeerID() + " adding local parameter: " + parameter);
				pSearch.addLocalParameter(parameter);
			}

			myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
			pSearch.commit();

		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " error loading data." + e.getMessage());
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
	}

	private String getUTableFilePath(final PeerID peerID) {
		return TEMP_DIR + File.separator + "UTable" + peerID + ".xml";
	}

	@Override
	public void printOutputs() {
		printMulticastTable();
	}

	@Override
	public void parametersFound(final SearchResponseMessage receivedMessage) {
		myLogger.info("Peer " + peer.getPeerID() + " found parameters " + receivedMessage.getParameters() + " in node " + receivedMessage.getSource() + " received \"" + receivedMessage.getPayload() + "\"");

		foundPeers.addPeer(receivedMessage.getSource());

		myLogger.info("Peer " + peer.getPeerID() + " enqueing multicast message to all found parameters " + receivedMessage.getParameters() + ": " + foundPeers);
		pSearch.sendMulticastMessage(foundPeers, new MessageStringPayload(peer.getPeerID(), "Hey, peers"));
	}

	@Override
	public PayloadMessage searchMessageReceived(final SearchMessage msg) {
		if (msg.getPayload() instanceof MessageString) {
			final MessageString strMsg = (MessageString) msg.getPayload();
			myLogger.info("Peer " + peer.getPeerID() + " received \"" + strMsg.toString() + "\" on node " + peer.getPeerID() + " from " + msg.getSource());
		}
		return new MessageStringPayload(peer.getPeerID(), "Hello, source");
	}

	@Override
	public void multicastMessageAccepted(final PeerID source, final PayloadMessage payload, final int distance) {
		myLogger.info("Peer " + peer.getPeerID() + " received \"" + payload.toString() + "\" on node " + peer.getPeerID() + " from " + source);
	}

	@Override
	public PayloadMessage parametersChanged(final PeerID neighbor, final Set<Parameter> addedParameters, final Set<Parameter> removedParameters, final Set<Parameter> removedLocalParameters, final Map<Parameter, DistanceChange> changedParameters,
			final PayloadMessage payload) {
		return new MessageStringPayload(peer.getPeerID(), "Table changed");
	}

	@Override
	public void changedParameterRoutes(final Map<MessageID, Set<Parameter>> changedParameterRoutes, final Set<MessageID> lostParameterRoutes, final Map<MessageID, MessageID> associatedRoutes) {
	}

	@Override
	public void changedSearchRoutes(final Map<MessageID, Set<Parameter>> changedSearchRoutes, final Set<MessageID> lostSearchRoutes) {
	}
}
