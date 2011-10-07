package graphcreation;

import graphcreation.collisionbased.CollisionGraphCreator;
import graphcreation.collisionbased.ServiceDistance;
import graphcreation.services.Service;
import graphcreation.services.ServiceList;

import java.io.File;
import java.io.FileOutputStream;
import java.util.Map;
import java.util.Set;

import multicast.MulticastMessageListener;

import org.apache.log4j.Logger;

import peer.message.PayloadMessage;
import peer.peerid.PeerID;

import common.CommonAgentJ;

public class Peer extends CommonAgentJ implements MulticastMessageListener, GraphCreationListener {

	private static final String ADD_SERVICE = "addService";
	private static final String REMOVE_SERVICE = "removeService";

	private static final String SERVICES_DIR = "services";

	private final GraphCreator graphCreation;

	private ServiceList findServices;

	private final Logger myLogger = Logger.getLogger(Peer.class);

	public Peer() {
		graphCreation = new CollisionGraphCreator(peer, this, this);
	}

	@Override
	protected boolean peerCommands(final String command, final String[] args) {
		if (command.equals(ADD_SERVICE)) {
			if (args.length > 0) {
				final ServiceList services = new ServiceList();
				for (final String arg : args) {
					final int index = Integer.parseInt(arg);
					final Service service = findServices.getService(index);
					if (service != null)
						services.addService(service);
					else
						myLogger.error("Peer " + peer.getPeerID() + " service with index " + index + " not found.");
				}
				graphCreation.manageLocalServices(services, new ServiceList());
				return true;
			}
			myLogger.error("Peer " + peer.getPeerID() + " " + ADD_SERVICE + " had no arguments");
		} else if (command.equals(REMOVE_SERVICE)) {
			if (args.length > 0) {
				final ServiceList services = new ServiceList();
				for (final String arg : args) {
					final Service service = graphCreation.getSDG().getService(arg + ":" + peer.getPeerID());
					if (service != null)
						services.addService(service);
					else
						myLogger.error("Peer " + peer.getPeerID() + " service with index " + arg + " not found.");
				}
				graphCreation.manageLocalServices(new ServiceList(), services);
				return true;
			}
			myLogger.error("Peer " + peer.getPeerID() + " " + REMOVE_SERVICE + " had no arguments");
		}
		return false;
	}

	@Override
	public void loadData() {
		try {
			findServices = new ServiceList(SERVICES_DIR + File.separator + "Services.xml", peer.getPeerID());

			final String xmlPath = getServicesFilePath(peer.getPeerID());
			final ServiceList addedServices = new ServiceList(xmlPath, peer.getPeerID());
			graphCreation.manageLocalServices(addedServices, new ServiceList());

		} catch (final Exception e) {
			e.printStackTrace();
		}
	}

	private String getServicesFilePath(final PeerID peerID) {
		return SERVICES_DIR + File.separator + "Services" + peerID + ".xml";
	}

	@Override
	public void printOutputs() {
		printGraph();
	}

	private void printGraph() {
		final String xmlPath = getGraphFilePath(peer.getPeerID());
		try {
			final FileOutputStream f = new FileOutputStream(xmlPath);
			graphCreation.getSDG().saveToXML(f);
			f.close();
		} catch (final Exception e) {
			e.printStackTrace();
		}
	}

	private String getGraphFilePath(final PeerID peerID) {
		return TEMP_DIR + File.separator + "Graph" + peerID + ".xml";
	}

	@Override
	public void multicastMessageAccepted(final PeerID source, final PayloadMessage payload, final int distance) {
	}

	@Override
	public void newSuccessors(final Map<Service, Set<ServiceDistance>> newSuccessors) {
	}

	@Override
	public void newAncestors(final Map<Service, Set<ServiceDistance>> newAncestors) {
	}

	@Override
	public void lostSuccessors(final Map<Service, Set<Service>> lostSuccessors) {
	}

	@Override
	public void lostAncestors(final Map<Service, Set<Service>> lostAncestors) {
	}

	@Override
	public void filterConnections(final Map<Service, Set<ServiceDistance>> foundRemoteSuccessors, final Map<Service, Set<ServiceDistance>> foundRemoteAncestors) {
	}
}
