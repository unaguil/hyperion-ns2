source ../../../common/WCommon.tcl

set nNodes 6

set finishTime 15.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	source ../../common/simple.tcl	
	
	$ns_ at 3.0 "$agents(4) agentj searchParameter I-1"
	$ns_ at 5.0 "$node_(2) setdest 2.2 5.0 5.0"
}


wireless_simulation $nNodes $finishTime multicast.Peer