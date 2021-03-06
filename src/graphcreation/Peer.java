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
package graphcreation;

import graphcreation.GraphCreator.GraphType;
import graphcreation.collisionbased.CollisionGraphCreator;
import graphcreation.collisionbased.ServiceDistance;
import graphcreation.services.Service;
import graphcreation.services.ServiceList;

import java.io.File;
import java.io.FileOutputStream;
import java.util.Map;
import java.util.Set;

import multicast.MulticastMessageListener;
import peer.ReliableBroadcastPeer;
import peer.message.BroadcastMessage;
import peer.peerid.PeerID;
import util.logger.Logger;

import common.CommonAgentJ;

public class Peer extends CommonAgentJ implements MulticastMessageListener, GraphCreationListener {

	private static final String ADD_SERVICE = "addService";
	private static final String REMOVE_SERVICE = "removeService";

	private static final String SERVICES_DIR = "services";

	private final GraphCreator graphCreation;

	private ServiceList findServices;

	private final Logger myLogger = Logger.getLogger(Peer.class);

	public Peer() {
		super(true);
		graphCreation = new CollisionGraphCreator(((ReliableBroadcastPeer)peer), this, this, GraphType.BIDIRECTIONAL);
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
					final Service service = graphCreation.getService(arg + ":" + peer.getPeerID());
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
			findServices = new ServiceList(SERVICES_DIR + File.separator + "Services.xml", peer.getPeerID(), graphCreation.getTaxonomy());

			final String xmlPath = getServicesFilePath(peer.getPeerID());
			final ServiceList addedServices = new ServiceList(xmlPath, peer.getPeerID(), graphCreation.getTaxonomy());
			graphCreation.manageLocalServices(addedServices, new ServiceList());

		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " error loading data." + e.getMessage());
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
			graphCreation.saveToXML(f);
			f.close();
		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " error writting output data." + e.getMessage());
		}
	}

	private String getGraphFilePath(final PeerID peerID) {
		return TEMP_DIR + File.separator + "Graph" + peerID + ".xml";
	}

	@Override
	public void multicastMessageAccepted(final PeerID source, final BroadcastMessage payload, final int distance, final boolean directBroadcast) {
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
