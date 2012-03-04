from GenericMeasure import GenericMeasure

import Units

class SentXXXYYYMessages(GenericMeasure):
	def __init__(self, messageClass, payloadClass, period, simulationTime):		
		GenericMeasure.__init__(self, r"DEBUG .*?  - Peer .*? sending " + messageClass + "\(" + payloadClass + "\).*? ([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
			
	def parseLine(self, line):
		self.parseInc(line)
		
