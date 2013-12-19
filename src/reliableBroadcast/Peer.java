/*
*
*   Copyright (c) 2012 Unai Aguilera
*
*   Licensed under the Apache License, Version 2.0 (the "License");
*   you may not use this file except in compliance with the License.
*   You may obtain a copy of the License at
*
*       http://www.apache.org/licenses/LICENSE-2.0
*
*   Unless required by applicable law or agreed to in writing, software
*   distributed under the License is distributed on an "AS IS" BASIS,
*   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*   See the License for the specific language governing permissions and
*   limitations under the License.
*
*  
*   Author: Unai Aguilera <gkalgan@gmail.com>
*/
package reliableBroadcast;

import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Random;
import java.util.Set;

import peer.CommunicationLayer;
import peer.RegisterCommunicationLayerException;
import peer.ReliableBroadcastPeer;
import peer.message.BroadcastMessage;
import peer.message.MessageString;
import peer.peerid.PeerID;
import util.WaitableThread;
import util.logger.Logger;

import common.CommonAgentJ;

public class Peer extends CommonAgentJ {
	
	private static final Map<String, Long> sentTimes = Collections.synchronizedMap(new HashMap<String, Long>()); 
	private static final Map<String, Long> lastTimeReceived = Collections.synchronizedMap(new HashMap<String, Long>());
	
	private class TestCommunicationLayer implements CommunicationLayer {
		
		private static final int START_TIME = 5000;
		private static final int MAX_PERIOD = 10000;
		private static final int MAX_SLEEP = 100;
		
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
				
				startTime = System.currentTimeMillis();
				
				while (!Thread.interrupted() && (System.currentTimeMillis() - startTime) <= MAX_PERIOD) {
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
				sentTimes.put(str, System.currentTimeMillis());
			}
		}
		
		private long startTime;
		
		private final Set<String> receivedMessages = new HashSet<String>();
		private final SendThread sendThread = new SendThread();

		@Override
		public void messageReceived(final BroadcastMessage message, final long receptionTime) {
			if (message instanceof MessageString) {
				final String str = ((MessageString) message).toString();
				
				lastTimeReceived.put(str, System.currentTimeMillis());

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
		}

		@Override
		public void stop() {
			sendThread.stopAndWait();
		}
		
		private void enqueueMessage(final String str) {
			final MessageString msgStr = new MessageString(peer.getPeerID(), ((ReliableBroadcastPeer)peer).getDetector().getCurrentNeighbors(), str);
			myLogger.debug("Peer " + peer.getPeerID() + " enqueing message");
			((ReliableBroadcastPeer)peer).enqueueBroadcast(msgStr, communicationLayer);
		}

		@Override
		public boolean merge(List<BroadcastMessage> waitingMessages, BroadcastMessage sendingMessage) {
			return false;
		}
	}
	
	private final TestCommunicationLayer communicationLayer = new TestCommunicationLayer();
	
	private final Logger myLogger = Logger.getLogger(Peer.class);
	
	public Peer() {
		super(true);
		final Set<Class<? extends BroadcastMessage>> messageClasses = new HashSet<Class<? extends BroadcastMessage>>();
		messageClasses.add(MessageString.class);
		try {
			peer.addCommunicationLayer(communicationLayer, messageClasses);
		} catch (final RegisterCommunicationLayerException e) {
			myLogger.error("Peer " + peer.getPeerID() + " had problem registering communication layer: " + e.getMessage());
		}
	} 

	@Override
	protected void printOutputs() {
		if (peer.getPeerID().equals(new PeerID("0"))) {
			long total = 0;
			int counter = 0;
			for (final Entry<String, Long> lastReception : lastTimeReceived.entrySet()) {
				total += lastReception.getValue().longValue() - sentTimes.get(lastReception.getKey()).longValue();
				counter++;
			}
			
			final float delay = total / (float) counter; 
			
			myLogger.info(sentTimes);
			myLogger.info(lastTimeReceived);
			
			myLogger.info("Peer " + peer.getPeerID() + " end to end delay: " + delay + " ms");
		}
	}

	@Override
	protected boolean peerCommands(String command, String[] args) {
		return true;
	}

	@Override
	protected void loadData() {}
}
