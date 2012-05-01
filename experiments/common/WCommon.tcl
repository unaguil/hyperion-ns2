#Utility commands to be used with ns simulator

proc neighbours {node_} {
	set list ""
	foreach x [$node_ neighbors] {
		append list "-"
		append list [$x node-addr]
	}
	return $list
}

# Create nNodes nodes
proc createNodes {nodes_ nNodes_} {
	global ns_
	upvar $nodes_ nodes
	
	for {set i 0} {$i < $nNodes_} {incr i} {
	  set nodes($i) [$ns_ node]
	}
}

proc createJavaAgents {nodes_ agents_} {
	global ns_
	upvar $nodes_ nodes
	upvar $agents_ agents
	
	for {set i 0} {$i < [array size nodes]} {incr i} {
		set agents($i) [new Agent/Agentj]
		$ns_ attach-agent $nodes($i) $agents($i)
	}
}

proc startupAgents {agents_ time_} {
	global ns_
	upvar $agents_ agents
	
	for {set i 0} {$i < [array size agents]} {incr i} {
		$ns_ at $time_ "$agents($i) startup"
	}
}

proc attachJavaObjects {agents_ time_ javaClass_} {
	global ns_
	upvar $agents_ agents
	
	for {set i 0} {$i < [array size agents]} {incr i} {
		$ns_ at $time_ "$agents($i) attach-agentj $javaClass_"
	}
}

proc initAgents {agents_ time_ nodes_} {
	global ns_
	upvar $agents_ agents
	upvar $nodes_ nodes
	
	for {set i 0} {$i < [array size agents]} {incr i} {
		$ns_ at $time_ "$agents($i) agentj init"
	}
}

proc shutdownAgents {agents_ time_} {
	global ns_
	upvar $agents_ agents
	
	for {set i 0} {$i < [array size agents]} {incr i} {
		$ns_ at $time_ "$agents($i) shutdown"
	}
}

proc stopAgents {agents_ time_} {
	global ns_
	upvar $agents_ agents
	
	for {set i 0} {$i < [array size agents]} {incr i} {
		$ns_ at $time_ "$agents($i) agentj stop"
	}
}

proc finish {} {
	global ns_
	$ns_ halt
	delete $ns_
}

proc static_simulation {nNodes finishTime javaAgent} {
	global ns_
	
	createNodes nodes $nNodes
	
	createLinks nodes

	puts "Creating JavaAgent NS2 agents and attach them to the nodes..." 
	createJavaAgents nodes agents

	puts "In script: Initializing agents  ..." 
	startupAgents agents 0.1

	puts "Setting Java Object to use by each agent ..." 
	attachJavaObjects agents 0.2 $javaAgent

	puts "Starting simulation ..." 
	initAgents agents 0.5 nodes

	do_something agents nodes

	stopAgents agents $finishTime

	$ns_ at $finishTime "$agents(0) agentj printStatistics"

	puts "Shutdown agents..."
	shutdownAgents agents [expr $finishTime + 1]
	
	$ns_ at [expr $finishTime + 2] "finish"

	$ns_ run
}

proc disableRandomMovement {nodes_} {
	global ns_
	upvar $nodes_ nodes
		
	for {set i 0} {$i < [array size nodes]} {incr i} {
		$nodes($i) random-motion 0
	}
} 

proc stop {} {
    global ns_ tracefd
    $ns_ flush-trace
    close $tracefd
}

proc wireless_simulation_extended {nNodes finishTime javaAgent nonDeterministic gridW gridH transmissionRange trace} {
	global ns_
	
	#$ns_ use-scheduler Heap #List, Heap, Calendar
	
	remove-all-packet-headers
	add-packet-header LL MAC IP
	
	if {$nonDeterministic} {
		puts "Setting non determistic behaviour"
		global defaultRNG
		$defaultRNG seed 0
	}
	
	if {$trace == ON} { 
		set cwd [pwd]
	
		set tracefd [open ${cwd}/tmp/trace w]
	} else {
		set tracefd [open /dev/null w]
	}
	
	$ns_ trace-all $tracefd
	
	set val(chan)           Channel/WirelessChannel    ;# channel type
	set val(prop)           Propagation/TwoRayGround   ;# radio-propagation model
	set val(netif)          Phy/WirelessPhy            ;# network interface type
	set val(mac)            Mac/802_11                 ;# MAC type
	set val(ifq)            Queue/DropTail/PriQueue    ;# interface queue type
	set val(ll)             LL                         ;# link layer type
	set val(ant)            Antenna/OmniAntenna        ;# antenna model
	set val(ifqlen)         5                          ;# max packet in ifq
	set val(rp)             DumbAgent                  ;# routing protocol
	
	Mac/802_11 set dataRate_ 54Mb
	Mac/802_11 set PreambleLength_ 72
	Agent/UDP set packetSize_ 1500
	
	set topo  [new Topography]

	$topo load_flatgrid $gridW $gridH

	set god_ [create-god $nNodes]

	$ns_ node-config -adhocRouting $val(rp) \
		 -llType $val(ll) \
		 -macType $val(mac) \
		 -ifqType $val(ifq) \
		 -ifqLen $val(ifqlen) \
		 -antType $val(ant) \
		 -propType $val(prop) \
		 -phyType $val(netif) \
		 -channelType $val(chan) \
		 -topoInstance $topo \
		 -agentTrace OFF \
		 -routerTrace OFF \
		 -macTrace $trace \
		 -movementTrace OFF \		
		 
	switch $transmissionRange {
		1 { Phy/WirelessPhy set RXThresh_ 0.000192278 } 
	    5 { Phy/WirelessPhy set RXThresh_ 7.69113e-06 }
	    10 { Phy/WirelessPhy set RXThresh_ 1.92278e-06 }
	    25 { Phy/WirelessPhy set RXThresh_ 3.07645e-07 }
	    50 { Phy/WirelessPhy set RXThresh_ 7.69113e-08 }
	    75 { Phy/WirelessPhy set RXThresh_ 3.41828e-08 }
	    100 { Phy/WirelessPhy set RXThresh_ 1.42681e-08 }
	    125 { Phy/WirelessPhy set RXThresh_ 5.8442e-09 }
	    150 { Phy/WirelessPhy set RXThresh_ 2.81838e-09 }
	    175 { Phy/WirelessPhy set RXThresh_ 1.52129e-09 }
	    200 { Phy/WirelessPhy set RXThresh_ 8.91754e-10 }
	    225 { Phy/WirelessPhy set RXThresh_ 5.56717e-10 }
	    250 { Phy/WirelessPhy set RXThresh_ 3.65262e-10 }
	    500 { Phy/WirelessPhy set RXThresh_ 2.28289e-11 }
	    1000 { Phy/WirelessPhy set RXThresh_ 1.42681e-12 }
	    default { 	puts "Invalid transmission range $transmissionRange"
	    			exit 
	    		} 
	}
	
	puts "Create nodes..."
	createNodes nodes $nNodes
	
	puts "Disable node random movement..."
	disableRandomMovement nodes

	puts "Creating JavaAgent NS2 agents and attach them to the nodes..." 
	createJavaAgents nodes agents
	
	puts "In script: Initializing agents  ..." 
	startupAgents agents 0.1
	
	puts "Setting Java Object to use by each agent ..." 
	attachJavaObjects agents 0.2 $javaAgent

	puts "Starting simulation ..." 
	set startTime 0.5
	initAgents agents $startTime nodes

	do_something agents nodes $god_
	
	set finishTime [expr $finishTime + $startTime]

	stopAgents agents $finishTime

	#wait some seconds for all threads finalization
	$ns_ at $finishTime "$agents(0) agentj printStatistics"

	puts "Shutdown agents..."
	shutdownAgents agents $finishTime
	$ns_ at $finishTime "stop"
	$ns_ at $finishTime "finish"
	
	$ns_ run
} 

proc wireless_simulation {nNodes finishTime javaAgent} {
	wireless_simulation_extended $nNodes $finishTime $javaAgent false 500 500 1 ON
}

