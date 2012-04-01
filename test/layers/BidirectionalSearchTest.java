package layers;

import graphcreation.graph.extendedServiceGraph.ExtendedServiceGraph;

import java.io.FileInputStream;

import taxonomy.Taxonomy;
import testing.BasicTest;
import testing.MultipleTests;

public class BidirectionalSearchTest extends MultipleTests {

	public BidirectionalSearchTest() throws Exception {
		super("files/BidirectionalSearch.xml", new GraphFileFilter());
	}

	@Override
	public Object readObject(final FileInputStream fileInputStream, Taxonomy taxonomy) throws Exception {
		final ExtendedServiceGraph graph = new ExtendedServiceGraph(taxonomy);
		graph.readFromXML(fileInputStream);
		return graph;
	}

	@Override
	public void check(final BasicTest test) throws Exception {
	}
}
