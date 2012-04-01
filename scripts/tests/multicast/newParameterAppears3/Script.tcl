source ../../../common/WCommon.tcl

set nNodes 10

set finishTime 20.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	source ../../common/searchParameter.tcl
	
	$ns_ at 3.0 "$agents(6) agentj searchParameter I-1 I-2"
	$ns_ at 8.0 "$agents(9) agentj searchParameter I-1"
	$ns_ at 12.0 "$agents(9) agentj searchParameter I-2"
	$ns_ at 15.0 "$agents(6) agentj addParameter I-1"
	$ns_ at 15.0 "$agents(9) agentj addParameter I-2"
}


wireless_simulation $nNodes $finishTime multicast.Peer
