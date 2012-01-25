from measures.generic.GenericMeasure import GenericMeasure
import measures.generic.Units as Units

import re

class InvalidRoutes(GenericMeasure):	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r'', period, simulationTime, Units.RATIO)
		
		self.__sentMulticastPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? sending remote multicast message .*? R:(\(.*?\)) .*? (\[.*?\]) ([0-9]+\,[0-9]+).*?')
		self.__acceptedMulticastPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer ([0-9]+) accepted multicast message .*? R:(\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')
		
		self.__multicastMessages = {}
		
		self.__total = 0
		
	def parseLine(self, line):
		m = self.__sentMulticastPattern.match(line)
		if m is not None:
			messageID = m.group(1)
			destinations = eval(m.group(2))
			time = float(m.group(3).replace(',','.'))
						
			self.__multicastMessages[messageID] = (destinations, time)
			self.__total += 1
				
			return 
		
		m = self.__acceptedMulticastPattern.match(line)
		if m is not None:
			destination = int(m.group(1))
			messageID = m.group(2)
			time = float(m.group(3).replace(',','.'))
			
			if messageID in self.__multicastMessages:
				destinations, time = self.__multicastMessages[messageID]
				destinations.remove(destination)
				if len(destinations) == 0:
					del self.__multicastMessages[messageID]
			return
		
	def getTotalValue(self):
		failedRoutes = 0
		for messageID, (destinations, time) in self.__multicastMessages.iteritems():
			failedRoutes += len(destinations)
		
		if self.__total > 0.0:
			return failedRoutes / float(self.__total)
		else:
			return 0.0
		
