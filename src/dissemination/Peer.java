package dissemination;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;

import peer.ReliableBroadcastPeer;
import peer.message.BroadcastMessage;
import peer.peerid.PeerID;
import taxonomy.parameter.InvalidParameterIDException;
import taxonomy.parameter.Parameter;
import taxonomy.parameter.ParameterFactory;
import taxonomy.parameterList.ParameterList;
import util.logger.Logger;

import common.CommonAgentJ;

import detection.NeighborEventsListener;
import dissemination.newProtocol.ParameterTableUpdater;

/**
 * This is an implementation of a peer which uses and tests the parameter
 * dissemination layer. It is intended for testing purposes.
 * 
 * @author Unai Aguilera (unai.aguilera@gmail.com)
 * 
 */
public class Peer extends CommonAgentJ implements TableChangedListener, NeighborEventsListener {

	private static final String REMOVE_PARAMETER = "removeParameter";

	private static final String ADD_PARAMETER = "addParameter";

	private static final String PARAMETERS_DIR = "parameters";

	private final ParameterDisseminator pDisseminator;

	private final Logger myLogger = Logger.getLogger(Peer.class);

	public Peer() {
		super(true);
		pDisseminator = new ParameterTableUpdater(((ReliableBroadcastPeer)peer), this);
	}

	@Override
	protected boolean peerCommands(final String command, final String[] args) {
		if (command.equals(ADD_PARAMETER)) {
			if (args.length > 0)
				try {
					for (final String arg : args) {
						final Parameter parameter = ParameterFactory.createParameter(arg, pDisseminator.getTaxonomy());
						myLogger.info("Peer " + peer.getPeerID() + " adding local parameter: " + parameter);
						pDisseminator.addLocalParameter(parameter);
					}

					myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
					pDisseminator.commit();

					return true;

				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
					return false;
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + ADD_PARAMETER + " had no arguments");
		} else if (command.equals(REMOVE_PARAMETER)) {
			if (args.length > 0)
				try {
					for (final String arg : args) {
						final Parameter parameter = ParameterFactory.createParameter(arg, pDisseminator.getTaxonomy());
						myLogger.info("Peer " + peer.getPeerID() + " removing local parameter: " + parameter);
						pDisseminator.removeLocalParameter(parameter);
					}

					myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
					pDisseminator.commit();

					return true;
				} catch (final InvalidParameterIDException ipe) {
					myLogger.error("Peer " + peer.getPeerID() + " processed invalid parameter. " + ipe.getMessage());
				}
			myLogger.error("Peer " + peer.getPeerID() + " " + REMOVE_PARAMETER + " had no arguments");
		}
		return false;
	}

	@Override
	public void loadData() {
		try {
			final String xmlPath = getParametersFilePath(peer.getPeerID());
			final ParameterList pList = new ParameterList(xmlPath, pDisseminator.getTaxonomy());

			myLogger.info("Peer " + peer.getPeerID() + " loading parameters: " + pList + " from file " + xmlPath);

			for (final Parameter parameter : pList.getParameterSet()) {
				myLogger.info("Peer " + peer.getPeerID() + " adding local parameter: " + parameter);
				pDisseminator.addLocalParameter(parameter);
			}

			myLogger.info("Peer " + peer.getPeerID() + " commiting local parameter changes");
			pDisseminator.commit();

		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " error loading data." + e.getMessage());
		}
	}

	private String getParametersFilePath(final PeerID peerID) {
		return PARAMETERS_DIR + File.separator + "Parameters" + peerID + ".xml";
	}

	private String getPTableFilePath(final PeerID peerID) {
		return TEMP_DIR + File.separator + "PTable" + peerID + ".xml";
	}

	public void printDisseminationTable() {
		final String xmlPath = getPTableFilePath(peer.getPeerID());
		try {
			final FileOutputStream f = new FileOutputStream(xmlPath);
			pDisseminator.saveToXML(f);
			f.close();
		} catch (final IOException ioe) {
			myLogger.error("Peer " + peer.getPeerID() + " error writting output data." + ioe.getMessage());
		}
	}

	@Override
	public void printOutputs() {
		printDisseminationTable();
	}

	@Override
	public void neighborsChanged(Set<PeerID> newNeighbors, Set<PeerID> lostNeighbors) {
	}

	@Override
	public BroadcastMessage parametersChanged(PeerID neighbor, Set<Parameter> newParameters, Set<Parameter> removedParameters, Set<Parameter> removedLocalParameters, Map<Parameter, DistanceChange> changedParameters, Set<Parameter> addedParameters,
			List<BroadcastMessage> payloadMessages) {
		return null;
	}
}
