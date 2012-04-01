source ../../../common/WCommon.tcl

set nNodes 4

set finishTime 15.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	source ../../common/loop.tcl
	
	$ns_ at 3.0 "$agents(1) agentj searchParameter I-1"		
}

wireless_simulation $nNodes $finishTime multicast.Peer