from GenericMeasure import GenericMeasure

import Units

class ReceivedPackets(GenericMeasure):
	""" Total number of received packets"""
	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG peer.BasicPeer  - Peer [0-9]+ received packet.*?([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
			
	def parseLine(self, line):
		self.parseInc(line)
