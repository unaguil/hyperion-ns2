import re

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgSearchTimeFirstOcurrence(GenericAvgMeasure):	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__startPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? started search for parameters (\[.*?\]) searchID (\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')
		self.__endPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? found parameters (\[.*?\]) in node ([0-9]+) searchID (\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')							 
		
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
			searchID = m.group(3)
			time = float(m.group(4).replace(',','.')) 
								
			if searchID in self.__currentSearches:
				self.periodicAvgValues.addValue(time - self.__currentSearches[searchID], time)
				del self.__currentSearches[searchID]
			
			return 	
