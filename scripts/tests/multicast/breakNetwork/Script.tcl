source ../../../common/WCommon.tcl

set nNodes 10

set finishTime 15.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	source ../../common/searchParameter.tcl
	
	$ns_ at 3.0 "$agents(6) agentj searchParameter I-A I-B"
	$ns_ at 3.0 "$agents(9) agentj searchParameter I-A"
	$ns_ at 5.0 "$agents(9) agentj searchParameter I-B"
	
	$ns_ at 7.0 "$node_(2) setdest 2.2 5.0 5.0"
}


wireless_simulation $nNodes $finishTime multicast.Peer
