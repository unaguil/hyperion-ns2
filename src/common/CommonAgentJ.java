package common;

import java.io.IOException;
import java.io.PrintStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketException;
import java.util.ArrayList;
import java.util.List;

import org.apache.log4j.Logger;

import peer.BasicPeer;
import peer.Peer;
import peer.PeerBehavior;
import peer.messagecounter.TotalMessageCounter;
import peer.peerid.PeerID;
import proto.logging.api.Logger.LogLevel;
import agentj.AgentJAgent;
import agentj.dns.Addressing;
import agentj.dns.AgentJNameService;

/**
 * This class defines the basic methods and functionality for the integration
 * with NS2/AgentJ. It provides methods for communication including message
 * sending and reception.
 * 
 * @author Unai Aguilera (unai.aguilera@gmail.com)
 * 
 */
public abstract class CommonAgentJ extends AgentJAgent implements PeerBehavior {

	// Used to set null output log for AgentJ library.
	public static final PrintStream NULL_PRINT_STREAM = null;

	// Directory used to output information
	protected static final String TEMP_DIR = "tmp";

	// local socket address
	private java.net.InetSocketAddress socketAddress;

	// Basic peer
	protected final Peer peer;

	private final Logger myLogger = Logger.getLogger(CommonAgentJ.class);

	// The UDP socket used by the peer for communication.
	private DatagramSocket socket;
	private byte[] data;

	private static final int SO_TIMEOUT = 5;

	// Default UDP port
	private static final int DEFAULT_PORT = 5555;

	// PeerAgentJ commands
	private static final String COMMAND_PRINT_STATISTICS = "printStatistics";
	private static final String COMMAND_STOP = "stop";
	private static final String COMMAND_INIT = "init";

	private static final int RECV_BUFF = 65536; // TODO Check this value

	/**
	 * Constructor of the PeerAgentJ class. This constructor is intended to be
	 * used with NS2 simulation.
	 * 
	 * @param msgCounter
	 *            counter object is passed during construction. It allows to
	 *            extend the basic functionality of message counter.
	 */
	public CommonAgentJ() {
		this.setNativeDebugLevel(AgentJDebugLevel.error);
		this.setJavaDebugLevel(LogLevel.ERROR);

		peer = new BasicPeer(this);
	}

	@Override
	public boolean command(final String command, final String[] args) {
		if (command.equals(COMMAND_INIT)) {
			// Initialize the peer using the host name information from NS2
			try {
				peer.initPeer(new PeerID(this.getNs2Node().getHostName()));
			} catch (IOException e) {
				e.printStackTrace();
				return false;
			}
			return true;
		} else if (command.equals(COMMAND_STOP)) {
			// Stop peer
			peer.stopPeer(); // Calls the delegated method
			return true;
		} else if (command.equals(COMMAND_PRINT_STATISTICS)) {
			// Output statistical information
			TotalMessageCounter.logStatistics();
			printOutputs();
			return true;
		}
		// If passed command is not one of the above, delegate processing
		if (!peerCommands(command, args)) {
			myLogger.error("Peer " + peer.getPeerID() + " error processing agentj command: " + command + " args: " + toString(args));
			return false;
		}
		return true;
	}

	@Override
	public void initCommunication() throws IOException {
		this.socket = new DatagramSocket(DEFAULT_PORT);
		this.data = new byte[RECV_BUFF];

		// Obtain the NS2 simulator broadcast address using the AgentJ API
		final String broadcastAddress = AgentJNameService.getIPAddress(Addressing.getNsBroadcastAddress());
		socketAddress = new java.net.InetSocketAddress(broadcastAddress, DEFAULT_PORT);
	}

	@Override
	public void broadcast(final byte[] data) throws IOException {
		// Create a new datagram packet and send it using the socket
		final DatagramPacket p = new DatagramPacket(data, data.length, socketAddress);
		socket.send(p);
	}

	@Override
	public byte[] receiveData() {
		// Creates the reception buffer and packet
		final DatagramPacket packet = new DatagramPacket(data, data.length);

		byte[] data = null;
		try {
			socket.setSoTimeout(SO_TIMEOUT);
			socket.receive(packet);
			data = packet.getData();
		} catch (SocketException e) {
		} catch (IOException e) {
		}

		return data;
	}

	private String toString(final String[] strArray) {
		final List<String> list = new ArrayList<String>();
		for (final String s : strArray)
			list.add(s);
		return list.toString();
	}

	protected abstract boolean peerCommands(String command, String[] args);

	protected abstract void printOutputs();
}
