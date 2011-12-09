package layers;

import java.io.File;
import java.io.FileFilter;
import java.io.FileInputStream;
import java.util.List;

import detection.NeighborDetector;
import detection.NeighborEventsListener;

import multicast.search.unicastTable.UnicastTable;
import peer.message.BroadcastMessage;
import peer.peerid.PeerID;
import peer.peerid.PeerIDSet;
import testing.BasicTest;
import testing.MultipleTests;

class UTableFileFilter implements FileFilter {

	@Override
	public boolean accept(final File file) {
		return file.getName().contains("UTable");
	}
}

public class MulticastTest extends MultipleTests {
	
	private static class DummyNeighborDetector implements NeighborDetector {

		@Override
		public void init() {}

		@Override
		public void stop() {}

		@Override
		public boolean checkWaitingMessages(List<BroadcastMessage> waitingMessages, BroadcastMessage sendingMessage) {
			return false;
		}

		@Override
		public void messageReceived(BroadcastMessage message, long receptionTime) {}

		@Override
		public PeerIDSet getCurrentNeighbors() {
			return new PeerIDSet();
		}

		@Override
		public void addNeighborListener(NeighborEventsListener listener) {}
		
	}
	
	private static final NeighborDetector nDetector = new DummyNeighborDetector();

	public MulticastTest() throws Exception {
		super("files/Multicast.xml", new UTableFileFilter());
	}

	@Override
	public Object readObject(final FileInputStream fileInputStream) throws Exception {
		final UnicastTable uTable = new UnicastTable(PeerID.VOID_PEERID, nDetector);
		uTable.readFromXML(fileInputStream);
		return uTable;
	}

	@Override
	public void check(final BasicTest test) throws Exception {
	}
}
