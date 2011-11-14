from GenericMeasure import GenericMeasure

import Units

class BroadcastedPackets(GenericMeasure):
	""" Total number of broadcasted messages of any type """
	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG peer.BasicPeer  - Peer [0-9]+ broadcasting.*?([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
			
	def parseLine(self, line):
		self.parseInc(line)
