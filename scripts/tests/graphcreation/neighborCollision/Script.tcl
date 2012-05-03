source ../../../common/WCommon.tcl

set nNodes 4

set finishTime 20.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	$node_(0) set X_ 100.0
	$node_(0) set Y_ 100.0
	$node_(0) set Z_ 0.0
	
	$node_(1) set X_ 99.75
	$node_(1) set Y_ 100.5
	$node_(1) set Z_ 0.0
	
	$node_(2) set X_ 100.25
	$node_(2) set Y_ 100.5
	$node_(2) set Z_ 0.0
	
	$node_(3) set X_ 100.0
	$node_(3) set Y_ 101.25
	$node_(3) set Z_ 0.0
	
	$ns_ at 8.0 "$node_(1) setdest 400.0 5.0 200.0"
}


wireless_simulation $nNodes $finishTime graphcreation.Peer
