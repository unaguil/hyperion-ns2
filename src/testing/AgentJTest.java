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
package testing;

import java.util.List;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetSocketAddress;
import java.net.SocketException;
import java.util.ArrayList;

import proto.logging.api.Logger.LogLevel;
import util.logger.Logger;
import agentj.AgentJAgent;
import agentj.dns.Addressing;
import agentj.dns.AgentJNameService;

public class AgentJTest extends AgentJAgent {

	private static final int PORT = 5555;
	
	private static final int NUM_THREADS = 10;

	private final Logger myLogger = Logger.getLogger(AgentJTest.class); 

	private static final String COMMAND_PRINT_OUTPUTS = "printStatistics";
	private static final String COMMAND_STOP = "stop";
	private static final String COMMAND_INIT = "init";

	private ReceivingThread receivingThread = null;
	private SendingThread sendingThread = null;

	private DatagramSocket socket = null;

	abstract class MyThread extends Thread {

		private boolean halted = false;

		protected final DatagramSocket socket;

		public MyThread(final DatagramSocket socket) {
			this.socket = socket;
		}

		protected synchronized boolean halted() {
			return halted;
		}

		public synchronized void halt() {
			halted = true;
		}
	}

	class ReceivingThread extends MyThread {

		private final byte[] data = new byte[256];

		public ReceivingThread(final DatagramSocket socket) {
			super(socket);
		}

		@Override
		public void run() {
			while (!halted()) {
				myLogger.debug("Peer " + getHost() + " thread running");

				final DatagramPacket packet = new DatagramPacket(data, data.length);

				try {
					socket.receive(packet);
					final String str = new String(packet.getData());
					myLogger.debug("Peer " + getHost() + " received string " + str);
				} catch (IOException e) {
					myLogger.error("Peer " + getHost() + " error receiving from socket. Cause: " + e.getMessage());
				}
			}
		}
	}

	class DummyThread extends Thread {

		private boolean halted = false;

		private final int id;

		public DummyThread(final int id) {
			this.id = id;
		}

		@Override
		public void run() {
			while (!halted()) {
				myLogger.debug("Peer " + getHost() + " executing dummy thread " + id);

				try {
					Thread.sleep(5);
				} catch (InterruptedException e) {

				}
			}
		}

		protected synchronized boolean halted() {
			return halted;
		}

		public synchronized void halt() {
			halted = true;
		}
	}

	class SendingThread extends MyThread {

		private final String address;

		public SendingThread(final DatagramSocket socket, final String address) {
			super(socket);
			this.address = address;
		}

		@Override
		public void run() {
			while (!halted()) {
				try {
					byte b[] = "Hola, mundo".getBytes();
					DatagramPacket p = new DatagramPacket(b, b.length, new InetSocketAddress(address, PORT));
					socket.send(p);
				} catch (SocketException e) {
					myLogger.debug("Peer " + getHost() + " socket sending error. Cause " + e.getMessage());
				} catch (IOException e) {
					myLogger.debug("Peer " + getHost() + " socket sending error. Cause " + e.getMessage());
				}

				try {
					Thread.sleep(5);
				} catch (InterruptedException e) {
					interrupt();
				}
			}
		}
	}

	public AgentJTest() {
		this.setNativeDebugLevel(AgentJDebugLevel.error);
		this.setJavaDebugLevel(LogLevel.ERROR);
	}

	private String getHost() {
		return getNs2Node().getHostName();
	}
	
	private final List<DummyThread> dummyThreads = new ArrayList<DummyThread>();

	private void initPeer() {
		myLogger.debug("Peer " + getHost() + " creating socket");
		try {
			socket = new DatagramSocket(PORT);

			receivingThread = new ReceivingThread(socket);
			receivingThread.start();

			final String broadcastAddress = AgentJNameService.getIPAddress(Addressing.getNsBroadcastAddress());
			sendingThread = new SendingThread(socket, broadcastAddress);
			sendingThread.start();
			
			for (int i = 0; i< NUM_THREADS; i++) {
				DummyThread dummyThread = new DummyThread(i);
				dummyThread.start();
				dummyThreads.add(dummyThread);
			}

		} catch (SocketException e) {
			myLogger.error("Peer " + getHost() + " got problem creating socket. Cause: " + e.getMessage());
		}
	}

	private void stopPeer() {
		for (final DummyThread dummyThread : dummyThreads) 
			dummyThread.halt();
		
		myLogger.debug("Peer " + getHost() + " all dummy threads stopped");
		
		myLogger.debug("Peer " + getHost() + " closing socket");
		socket.close();

		receivingThread.halt();
		myLogger.debug("Peer " + getHost() + " receiving thread stopped");

		sendingThread.halt();
		myLogger.debug("Peer " + getHost() + " sending thread stopped");
	}

	@Override
	public boolean command(String command, String[] args) {
		if (command.equals(COMMAND_INIT)) {
			// Initialize the peer using the host name information from NS2
			myLogger.debug("Peer " + getHost() + " initializing");
			initPeer();
			return true;
		} else if (command.equals(COMMAND_STOP)) {
			myLogger.debug("Peer " + getHost() + " stopping");
			stopPeer();
			return true;
		} else if (command.equals(COMMAND_PRINT_OUTPUTS)) {
			return true;
		}

		return true;
	}
}
