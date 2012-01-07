package reliableBroadcast;

import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

import peer.CommunicationLayer;
import peer.RegisterCommunicationLayerException;
import peer.message.BroadcastMessage;
import peer.message.MessageString;
import util.WaitableThread;
import util.logger.Logger;

import common.CommonAgentJ;

public class Peer extends CommonAgentJ {
	
	private class TestCommunicationLayer implements CommunicationLayer {
		
		private static final int START_TIME = 5000;
		private static final int MAX_TIME = 10000;
		private static final int MAX_SLEEP = 1000;
		
		class SendThread extends WaitableThread {
			
			private int counter = 0;
			
			private final Random r = new Random();
			
			@Override
			public void run() {
				
				try {
					WaitableThread.sleep(START_TIME);
				} catch (InterruptedException e) {
					interrupt();
				}
				
				while (!Thread.interrupted() && (System.currentTimeMillis() - startTime) <= MAX_TIME) {
					final int sleepTime = r.nextInt(MAX_SLEEP);
					
					sendMessage(peer.getPeerID() + "-" + counter);
					counter++;
					
					if (sleepTime > 0) {
						try {
							WaitableThread.sleep(sleepTime);
						} catch (InterruptedException e) {
							interrupt();
						}
					}
				}
			}
			
			public void sendMessage(final String str) {
				myLogger.debug("Peer " + peer.getPeerID() + " sending string " + str);
				enqueueMessage(str);
				receivedMessages.add(str);
			}
		}
		
		private long startTime;
		
		private final Set<String> receivedMessages = new HashSet<String>();
		private final SendThread sendThread = new SendThread();

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
			sendThread.start();
			startTime = System.currentTimeMillis();
		}

		@Override
		public void stop() {
			sendThread.stopAndWait();
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
