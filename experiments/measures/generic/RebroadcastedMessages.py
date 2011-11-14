from GenericMeasure import GenericMeasure

import Units

class RebroadcastedMessages(GenericMeasure):
	"""Total number of rebroadcasted messages"""
	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG peer.ReliableBroadcast  - Peer [0-9]+ rebroadcasted message.*? ([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
	
	def parseLine(self, line):
		self.parseInc(line)
		