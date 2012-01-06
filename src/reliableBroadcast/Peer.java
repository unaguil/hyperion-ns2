package reliableBroadcast;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import peer.CommunicationLayer;
import peer.RegisterCommunicationLayerException;
import peer.message.BroadcastMessage;
import peer.message.MessageString;
import util.logger.Logger;
import util.timer.Timer;
import util.timer.TimerTask;

import common.CommonAgentJ;

public class Peer extends CommonAgentJ {
	
	private class TestCommunicationLayer implements CommunicationLayer, TimerTask {
		
		private static final int PERIOD = 5000;
		private static final int MAX_TIME = 10000;
		
		private final Timer timer = new Timer(PERIOD, this);
		private long startTime;
		
		private final Set<String> receivedMessages = new HashSet<String>();

		@Override
		public void messageReceived(final BroadcastMessage message, final long receptionTime) {
			if (message instanceof MessageString) {
				final String str = ((MessageString) message).toString();
				
				if (!receivedMessages.contains(str)) {
					enqueueMessage(str);
					receivedMessages.add(str);
				}
			}
		}

		@Override
		public void init() {
			myLogger.debug("Peer " + peer.getPeerID() + " starting timer");
			timer.start();
			startTime = System.currentTimeMillis();
		}

		@Override
		public void stop() {
			timer.stopAndWait();
		}
		
		public void perform() {
			if ((System.currentTimeMillis() - startTime) <= MAX_TIME) {
				enqueueMessage(peer.getPeerID().toString());
				receivedMessages.add(peer.getPeerID().toString());
			}
		}
		
		private void enqueueMessage(final String str) {
			final MessageString msgStr = new MessageString(peer.getPeerID(), peer.getDetector().getCurrentNeighbors().getPeerSet(), str);
			myLogger.debug("Peer " + peer.getPeerID() + " enqueing message");
			peer.enqueueBroadcast(msgStr, communicationLayer);
		}

		@Override
		public BroadcastMessage isDuplicatedMessage(List<BroadcastMessage> waitingMessages, BroadcastMessage sendingMessage) {
			return null;
		}
	}
	
	private final TestCommunicationLayer communicationLayer = new TestCommunicationLayer();
	
	private final Logger myLogger = Logger.getLogger(Peer.class);
	
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
	protected void printOutputs() {}

	@Override
	protected boolean peerCommands(String command, String[] args) {
		return true;
	}

	@Override
	protected void loadData() {}
}
