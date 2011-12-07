package detection;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import util.logger.Logger;

import peer.CommunicationLayer;
import peer.RegisterCommunicationLayerException;
import peer.message.BroadcastMessage;
import peer.message.MessageString;
import peer.peerid.PeerID;
import peer.peerid.PeerIDSet;

import common.CommonAgentJ;

/**
 * This is an implementation of a peer which only provides reliable broadcast
 * and neighbor detection. The node has flood mode that when set starts to
 * broadcast message periodically. It is intended for testing purposes.
 * 
 * @author Unai Aguilera (unai.aguilera@gmail.com)
 * 
 */
public class Peer extends CommonAgentJ implements NeighborEventsListener {

	private static class DumbCommunicationLayer implements CommunicationLayer {

		@Override
		public void messageReceived(final BroadcastMessage message, final long receptionTime) {
		}

		@Override
		public void init() {
		}

		@Override
		public void stop() {
		}

		@Override
		public boolean checkWaitingMessages(List<BroadcastMessage> waitingMessages, BroadcastMessage sendingMessage) {
			return true;
		}
	}
	
	private final DumbCommunicationLayer communicationLayer = new DumbCommunicationLayer();

	private final Logger myLogger = Logger.getLogger(Peer.class);

	/**
	 * Constructs the detection layer peer.
	 */
	public Peer() {
		final Set<Class<? extends BroadcastMessage>> messageClasses = new HashSet<Class<? extends BroadcastMessage>>();
		messageClasses.add(MessageString.class);
		try {
			peer.addCommunicationLayer(communicationLayer, messageClasses);
		} catch (final RegisterCommunicationLayerException e) {
			myLogger.error("Peer " + peer.getPeerID() + " had problem registering communication layer: " + e.getMessage());
		}
	}
	
	@Override
	public void initComm() throws IOException {
		super.initComm();
		
		peer.getDetector().addNeighborListener(this);
	}

	@Override
	protected boolean peerCommands(final String command, final String[] args) {
		if (command.equals("broadcast")) {
			final List<PeerID> currentNeighbors = new ArrayList<PeerID>(peer.getDetector().getCurrentNeighbors().getPeerSet());
			final MessageString msgStr = new MessageString(peer.getPeerID(), currentNeighbors, new String(new byte[1]));
			peer.enqueueBroadcast(msgStr, communicationLayer);
			return true;
		}
		return false;
	}

	@Override
	public void loadData() {
	}

	private String getNeighbourListPath(final PeerID peerID) {
		return CommonAgentJ.TEMP_DIR + File.separator + "Neighbours" + peerID + ".xml";
	}

	public void printNeighbourList() {
		final String xmlPath = getNeighbourListPath(peer.getPeerID());
		try {
			final FileOutputStream f = new FileOutputStream(xmlPath);
			peer.getDetector().getCurrentNeighbors().saveToXML(f);
			f.close();
		} catch (final IOException e) {
			myLogger.error("Peer " + peer.getPeerID() + " had problem printing neighbor list: " + e.getMessage());
		}
	}

	@Override
	public void printOutputs() {
		printNeighbourList();
	}

	@Override
	public void appearedNeighbors(final PeerIDSet neighbours) {
	}

	@Override
	public void dissapearedNeighbors(final PeerIDSet neighbours) {
	}
}
