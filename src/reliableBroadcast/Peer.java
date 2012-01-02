package reliableBroadcast;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import peer.CommunicationLayer;
import peer.RegisterCommunicationLayerException;
import peer.message.BroadcastMessage;
import peer.message.MessageString;
import util.WaitableThread;
import util.logger.Logger;
import util.timer.Timer;
import util.timer.TimerTask;

import common.CommonAgentJ;

public class Peer extends CommonAgentJ {
	
	private class TestCommunicationLayer implements CommunicationLayer, TimerTask {
		
		class StopTimerThread extends WaitableThread {
			
			@Override
			public void run() {
				try {
					Thread.sleep(10000);
				} catch (InterruptedException e) {
					interrupt();
				}
				
				timer.stopAndWait();
			}
		}
		
		private static final int PERIOD = 1000;
		
		private final Timer timer = new Timer(PERIOD, this);
		
		private final StopTimerThread stopThread = new StopTimerThread();

		@Override
		public void messageReceived(final BroadcastMessage message, final long receptionTime) {
		}

		@Override
		public void init() {
			timer.start();
			
			stopThread.start();
		}

		@Override
		public void stop() {
			stopThread.stopAndWait();
			timer.stopAndWait();
		}
		
		public void perform() {
			final MessageString msgStr = new MessageString(peer.getPeerID(), peer.getDetector().getCurrentNeighbors().getPeerSet(), "Hello, world");
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
