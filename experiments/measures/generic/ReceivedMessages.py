from GenericMeasure import GenericMeasure

import Units

class ReceivedMessages(GenericMeasure):
	"""Total number of received messages of any type"""
	"""Due to broadcast issues received package number can be greater than BroadcastedMessages""" 
	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG peer.BasicPeer  - Peer [0-9]+ received .*? ([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
	
	def parseLine(self, line):
		self.parseInc(line)
		
			