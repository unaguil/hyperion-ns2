source ../../../common/WCommon.tcl

set nNodes 14

set finishTime 15.0

set ns_		[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_

	source ../../common/searchNotDiscard.tcl
	
	$ns_ at 3.0 "$agents(5) agentj searchParameterGeneric I-A"
}


wireless_simulation $nNodes $finishTime multicast.Peer
