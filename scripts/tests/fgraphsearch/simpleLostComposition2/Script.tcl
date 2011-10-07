source ../../../common/WCommon.tcl

set nNodes 6

set finishTime 25.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	source ../../common/simple.tcl
	
	$ns_ at 3.0 "$agents(3) agentj composeService 0"
	
	$ns_ at 8.0 "$node_(0) setdest 5.0 2.0 5.0"
}

wireless_simulation $nNodes $finishTime graphsearch.ForwardPeer
