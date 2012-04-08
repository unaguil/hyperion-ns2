import re

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgDiscoveryTimeFirstOcurrence(GenericAvgMeasure):	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__startPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? started search for parameters (\[.*?\]) searchID (\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')
		self.__endPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer [0-9]+ accepted multicast.search.message.SearchMessage (\(.*?\)) distance .*? parameters \[.*?\] ([0-9]+\,[0-9]+).*?')							 
		
		self.__currentSearches = {}
	
	def __getParameters(self, str):
		return [str.strip() for str in str[1:-1].split(',')]

	def parseLine(self, line):
		m = self.__startPattern.match(line)
		if m is not None:
			searchID = m.group(2)
			time = float(m.group(3).replace(',','.'))	
			self.__currentSearches[searchID] = time
			return
		
		m = self.__endPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			time = float(m.group(2).replace(',','.')) 
								
			if searchID in self.__currentSearches:
				self.periodicAvgValues.addValue(time - self.__currentSearches[searchID], time)
				del self.__currentSearches[searchID]
			
			return 	
