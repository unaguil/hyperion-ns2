from GenericMeasure import GenericMeasure
from GenericAvgMeasure import GenericAvgMeasure

import Units

class DeliveredMessages(GenericMeasure):
	def __init__(self, period, simulationTime, broadcastTable):
		GenericMeasure.__init__(self, r"DEBUG peer.ReliableBroadcast  - Peer [0-9]+ delivered message (\(.*?\)) ([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
		
		self.__broadcastTable = broadcastTable
		
	def parseInc(self, line):
		m = self.getProg().match(line)
		if m is not None:
			messageID = m.group(1)			
			startTime = self.__broadcastTable[messageID]
			time  = float(m.group(2).replace(',','.'))
			return (startTime, time)
			
class ReliableBroadcastedMessages(GenericMeasure):	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG peer.ReliableBroadcast  - Peer [0-9]+ reliable broadcasting message (\(.*?\)).*?([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
		
		self.__broadcastTable = {}
	
	def parseInc(self, line):
		m = self.getProg().match(line)
		if m is not None:
			messageID = m.group(1)		
			time  = float(m.group(2).replace(',','.'))
			self.__broadcastTable[messageID] = time
			
	def getBroadcastTable(self):
		return self.__broadcastTable

class DeliveringTime(GenericAvgMeasure):
	"""The average time used to deliver a message"""	
	
	def __init__(self, period, simulationTime):	
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__broadcastedMessages = ReliableBroadcastedMessages(period, simulationTime)
		self.__deliveredMessages = DeliveredMessages(period, simulationTime, self.__broadcastedMessages.getBroadcastTable()) 
	
	def parseLine(self, line):
		self.__broadcastedMessages.parseInc(line)
		result = self.__deliveredMessages.parseInc(line)
		if result is not None:
			broadcastTime, deliveredTime = result
			elapsedTime = deliveredTime - broadcastTime
			self.periodicAvgValues.addValue(elapsedTime, broadcastTime)
