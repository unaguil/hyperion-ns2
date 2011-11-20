package graphsearch;

public class ForwardPeerGraphCreationDisabled extends Peer {

	public ForwardPeerGraphCreationDisabled() {
		super(SearchMode.FORWARD);
		disableGraphCreationLayer();
	}
}
