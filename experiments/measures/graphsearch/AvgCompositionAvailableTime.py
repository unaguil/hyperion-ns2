import re
import numpy

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgCompositionAvailableTime(GenericAvgMeasure):
	"""Average time compositions are available"""
	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__foundPattern = re.compile('DEBUG .*?  - Peer [0-9]+ received composition for search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		self.__lostPattern = re.compile('DEBUG .*?  - Peer [0-9]+ received invalid composition for search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		
		self.__searches = {}
	
	def parseLine(self, line):
		m = self.__foundPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			time = float(m.group(2).replace(',','.'))
			
			if not searchID in self.__searches: 
				self.__searches[searchID] = time
		
			return
		
		m = self.__lostPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			invalidTime = float(m.group(2).replace(',','.'))			
			
			if searchID in self.__searches:
				foundTime = self.__searches[searchID]
				elapsedTime = invalidTime - foundTime
				self.periodicAvgValues.addValue(elapsedTime, foundTime) 
				del self.__searches[searchID]
			
			return
		 
	def finish(self):
		for searchID, foundTime in self.__searches.items():
			self.periodicAvgValues.addValue(self.getSimulationTime(), foundTime)
			