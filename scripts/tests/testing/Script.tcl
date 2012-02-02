source ../../common/WCommon.tcl

set nNodes 200

set finishTime 15.0

set ns_	[new Simulator]

proc do_something {agents_ nodes_ god_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ node_
}


wireless_simulation $nNodes $finishTime testing.AgentJTest
