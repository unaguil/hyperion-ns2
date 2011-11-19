package graphsearch;

public class ForwardPeerMulticastDisabled extends Peer {

	public ForwardPeerMulticastDisabled() {
		super(SearchMode.FORWARD);
		disableMulticastLayer();
	}
}
