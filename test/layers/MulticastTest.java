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
package layers;

import java.io.File;
import java.io.FileFilter;
import java.io.FileInputStream;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import multicast.search.unicastTable.UnicastTable;
import peer.message.BroadcastMessage;
import peer.peerid.PeerID;
import taxonomy.Taxonomy;
import testing.BasicTest;
import testing.MultipleTests;
import detection.NeighborDetector;
import detection.NeighborEventsListener;

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
		public boolean merge(List<BroadcastMessage> waitingMessages, BroadcastMessage sendingMessage) {
			return false;
		}

		@Override
		public void messageReceived(BroadcastMessage message, long receptionTime) {}

		@Override
		public Set<PeerID> getCurrentNeighbors() {
			return Collections.emptySet();
		}

		@Override
		public void addNeighborListener(NeighborEventsListener listener) {

		}
		
	}
	
	private static final NeighborDetector nDetector = new DummyNeighborDetector();

	public MulticastTest() throws Exception {
		super("files/Multicast.xml", new UTableFileFilter());
	}

	@Override
	public Object readObject(final FileInputStream fileInputStream, Taxonomy taxonomy) throws Exception {
		final UnicastTable uTable = new UnicastTable(PeerID.VOID_PEERID, nDetector, taxonomy);
		uTable.readFromXML(fileInputStream);
		return uTable;
	}

	@Override
	public void check(final BasicTest test) throws Exception {
	}
}
