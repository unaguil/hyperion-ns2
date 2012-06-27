source ../../../common/WCommon.tcl

set nNodes 3

set finishTime 15.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	$node_(0) set X_ 100.0
	$node_(0) set Y_ 100.0
	$node_(0) set Z_ 0.0

	$node_(1) set X_ 400.0
	$node_(1) set Y_ 400.0
	$node_(1) set Z_ 0.0

	$node_(2) set X_ 400.0
	$node_(2) set Y_ 0.0
	$node_(2) set Z_ 0.0

	$ns_ at 3.0 "$agents(0) agentj searchParameter I-1"
	$ns_ at 5.0 "$node_(1) setdest 99.5 100.5 100.0"
	$ns_ at 7.0 "$node_(2) setdest 100.5 100.5 100.0"
	
	$ns_ at 12.0 "$node_(0) setdest 100.7 100.5 100.0"
}


wireless_simulation $nNodes $finishTime multicast.Peer
