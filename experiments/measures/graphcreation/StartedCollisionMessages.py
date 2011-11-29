from measures.generic.GenericMeasure import GenericMeasure

import measures.generic.Units as Units

class StartedCollisionMessages(GenericMeasure):	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG .*?  - Peer .*? starting collision message while searching for parameters.*? ([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
			
	def parseLine(self, line):
		self.parseInc(line)
		
