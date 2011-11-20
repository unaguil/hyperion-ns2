package graphsearch;

import graphcreation.graph.extendedServiceGraph.ExtendedServiceGraph;
import graphcreation.services.Service;
import graphcreation.services.ServiceList;
import graphsearch.backward.BackwardCompositionSearch;
import graphsearch.bidirectionalsearch.BidirectionalSearch;
import graphsearch.commonCompositionSearch.CommonCompositionSearch;
import graphsearch.forward.ForwardCompositionSearch;
import graphsearch.util.Utility;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import peer.peerid.PeerID;
import util.logger.Logger;

import common.CommonAgentJ;

public abstract class Peer extends CommonAgentJ implements CompositionListener {

	private static final String SERVICES_DIR = "services";

	private final CompositionSearch compositionSearch;

	private ServiceList findServices;

	private final Map<SearchID, List<ExtendedServiceGraph>> receivedCompositions = new ConcurrentHashMap<SearchID, List<ExtendedServiceGraph>>();

	private final Logger myLogger = Logger.getLogger(Peer.class);

	private static final String COMPOSE_SERVICE = "composeService";

	private static final String ADD_SERVICE = "addService";
	private static final String REMOVE_SERVICE = "removeService";

	public enum SearchMode {
		FORWARD, BACKWARD, BIDIRECTIONAL
	}

	public Peer(final SearchMode searchMode) {
		switch (searchMode) {
		case BACKWARD:
			compositionSearch = new BackwardCompositionSearch(peer, this);
			break;
		case BIDIRECTIONAL:
			compositionSearch = new BidirectionalSearch(peer, this);
			break;
		default:
			compositionSearch = new ForwardCompositionSearch(peer, this);
			break;
		}
	}
	
	public void disableMulticastLayer() {
		((CommonCompositionSearch)compositionSearch).disableMulticastLayer();
	}
	
	public void disableGraphCreationLayer() {
		((CommonCompositionSearch)compositionSearch).disableGraphCreationLayer();
	}

	@Override
	protected boolean peerCommands(final String command, final String[] args) {
		if (command.equals(COMPOSE_SERVICE)) {
			if (args.length == 1) {
				final int index = Integer.parseInt(args[0]);
				final Service searchedService = findServices.getService(index);
				final SearchID searchID = compositionSearch.startComposition(searchedService);
				receivedCompositions.put(searchID, new ArrayList<ExtendedServiceGraph>());
				return true;
			}
			myLogger.error("Peer " + peer.getPeerID() + " " + COMPOSE_SERVICE + " must have one argument");
		}
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
				compositionSearch.manageLocalServices(services, new ServiceList());
				return true;
			}
			myLogger.error("Peer " + peer.getPeerID() + " " + ADD_SERVICE + " had no arguments");
		} else if (command.equals(REMOVE_SERVICE)) {
			if (args.length > 0) {
				final ServiceList services = new ServiceList();
				for (final String arg : args) {
					final Service service = compositionSearch.getService(arg + ":" + peer.getPeerID());
					if (service != null)
						services.addService(service);
					else
						myLogger.error("Peer " + peer.getPeerID() + " service with index " + arg + " not found.");
				}
				compositionSearch.manageLocalServices(new ServiceList(), services);
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
			final ServiceList sList = new ServiceList(xmlPath, peer.getPeerID());
			compositionSearch.manageLocalServices(sList, new ServiceList());

		} catch (final Exception e) {
			myLogger.error("Peer " + peer.getPeerID() + " error loading data." + e.getMessage());
		}
	}

	private String getServicesFilePath(final PeerID peerID) {
		return SERVICES_DIR + File.separator + "Services" + peerID + ".xml";
	}

	private String getCompositionFilePath(final PeerID peerID) {
		return TEMP_DIR + File.separator + "Graph" + peerID + ".xml";
	}

	@Override
	public void printOutputs() {
		// merge all received compositions and obtain solution
		if (!receivedCompositions.isEmpty()) {
			final List<ExtendedServiceGraph> partialCompositions = new ArrayList<ExtendedServiceGraph>();
			synchronized (receivedCompositions) {
				partialCompositions.addAll(receivedCompositions.values().iterator().next());
			}
			
			if (!partialCompositions.isEmpty()) {
				final ExtendedServiceGraph finalComposition = mergePartialCompositions(partialCompositions);

				final String xmlPath = getCompositionFilePath(peer.getPeerID());
				try {
					final FileOutputStream f = new FileOutputStream(xmlPath);
					finalComposition.saveToXML(f);
					f.close();
				} catch (final Exception e) {
					myLogger.error("Peer " + peer.getPeerID() + " error writting output data." + e.getMessage());
				}
			}
		}
	}

	private ExtendedServiceGraph mergePartialCompositions(final List<ExtendedServiceGraph> compositions) {
		final ExtendedServiceGraph finalComposition = new ExtendedServiceGraph(compositions.get(0).getTaxonomy());
		for (final ExtendedServiceGraph composition : compositions)
			finalComposition.merge(composition);
		return finalComposition;
	}

	@Override
	public void compositionFound(final ExtendedServiceGraph composition, final SearchID searchID) {
		receivedCompositions.get(searchID).add(composition);
	}

	@Override
	public void compositionsLost(final SearchID searchID, final ExtendedServiceGraph invalidComposition) {
		// remove invalid composition from received ones
		for (final Iterator<ExtendedServiceGraph> it = receivedCompositions.get(searchID).iterator(); it.hasNext();) {
			final ExtendedServiceGraph composition = it.next();
			for (final Service service : invalidComposition.getServices())
				composition.removeService(service);

			// check if composition is valid
			boolean valid = false;
			for (final Service service : composition.getServices())
				// check if composition contains a GOAL service
				if (Utility.isGoalService(service))
					valid = true;

			if (!valid)
				it.remove();
		}
	}

	@Override
	public void compositionModified(final SearchID searchID, final Set<Service> removedServices) {
		for (final ExtendedServiceGraph composition : receivedCompositions.get(searchID))
			for (final Service service : removedServices)
				composition.removeService(service);
	}

	@Override
	public void compositionTimeExpired(final SearchID searchID) {
		myLogger.info("Peer " + peer.getPeerID() + " search " + searchID + " expired. " + receivedCompositions.get(searchID).size() + " compositions received");
	}
}
