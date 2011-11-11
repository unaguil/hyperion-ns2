from GenericMeasure import GenericMeasure
from measures.periodicValues.PeriodicValues import *

import Units

class DeliveredMessages(GenericMeasure):
	"""Total number of messages which were correctly delivered using reliable broadcast functionality stored in the sent time period"""
	
	def __init__(self, period, simulationTime, broadcastTable):
		GenericMeasure.__init__(self, r"DEBUG peer.ReliableBroadcast  - Peer [0-9]+ delivered message (\(.*?\)).*?", period, simulationTime, Units.MESSAGES)
		
		self.__broadcastTable = broadcastTable
		
	def parseInc(self, line):
		m = self.getProg().match(line)
		if m is not None:
			messageID = m.group(1)			
			time = self.__broadcastTable[messageID]
			self.incValue(time, self.getSimulationTime())
			
class ReliableBroadcastedMessages(GenericMeasure):
	"""Total number of messages sent using the reliable broadcast functionality"""
	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG peer.ReliableBroadcast  - Peer [0-9]+ reliable broadcasting message (\(.*?\)).*?([0-9]+\,[0-9]+).*?", period, simulationTime, Units.MESSAGES)
		
		self.__broadcastTable = {}
	
	def parseInc(self, line):
		m = self.getProg().match(line)
		if m is not None:
			messageID = m.group(1)			 
			time  = float(m.group(2).replace(',','.'))
			self.incValue(time, self.getSimulationTime())
			self.__broadcastTable[messageID] = time
			
	def getBroadcastTable(self):
		return self.__broadcastTable

class DeliveredRatio(GenericMeasure):
	"""The ratio of messages which were correctly delivered calculated using the sum of delivered and expired messages as the total number of messages"""	
	
	def __init__(self, period, simulationTime):	
		GenericMeasure.__init__(self, '', period, simulationTime, Units.RATIO)
		
		self.__period = period
		self.__simulationTime = simulationTime
		
		self.__broadcastedMessages = ReliableBroadcastedMessages(period, simulationTime)
		self.__deliveredMessages = DeliveredMessages(period, simulationTime, self.__broadcastedMessages.getBroadcastTable()) 
	
	def parseLine(self, line):
		self.__broadcastedMessages.parseInc(line)
		self.__deliveredMessages.parseInc(line)
			
	def getTotalValue(self):
		totalBroadcastedMessages = self.__broadcastedMessages.getTotalValue()
		if totalBroadcastedMessages == 0:
			return 0
		else:
			return self.__deliveredMessages.getTotalValue() / float(totalBroadcastedMessages)
		
	def getValues(self):
		values = PeriodicValues(0, self.__period, self.__simulationTime)
		
		broadcastedMessagesArray = self.__broadcastedMessages.getValues()
		deliveredMessagesArray = self.__deliveredMessages.getValues()
		
		for index in xrange(len(broadcastedMessagesArray)):
			broadcasted = broadcastedMessagesArray.getValue(index)
			delivered = deliveredMessagesArray.getValue(index)
			if broadcasted == 0:
				values.setValue(index, 0);
			else:
				values.setValue(index, delivered / float(broadcasted))
			 
		return values