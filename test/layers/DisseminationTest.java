package layers;

import java.io.File;
import java.io.FileFilter;
import java.io.FileInputStream;

import peer.peerid.PeerID;
import taxonomy.Taxonomy;
import testing.BasicTest;
import testing.MultipleTests;
import dissemination.newProtocol.ptable.DisseminationDistanceInfo;
import dissemination.newProtocol.ptable.ParameterTable;

class PTableFileFilter implements FileFilter {

	@Override
	public boolean accept(final File file) {
		return file.getName().contains("PTable");
	}
}

public class DisseminationTest extends MultipleTests {
	
	static class DisseminationDistance implements DisseminationDistanceInfo {
		
		private final int DDISTANCE = 5;

		@Override
		public int getMaxDistance() {
			return DDISTANCE;
		}
	}
	
	private static final DisseminationDistanceInfo disseminationInfo = new DisseminationDistance();

	public DisseminationTest() throws Exception {
		super("files/Dissemination.xml", new PTableFileFilter());
	}

	@Override
	public Object readObject(final FileInputStream fileInputStream, Taxonomy taxonomy) throws Exception {
		final ParameterTable pTable = new ParameterTable(disseminationInfo, PeerID.VOID_PEERID, taxonomy);
		pTable.readFromXML(fileInputStream);
		return pTable;
	}

	@Override
	public void check(final BasicTest test) throws Exception {
	}
}
