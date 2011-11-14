import re
import numpy

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgCompositionSearchTime(GenericAvgMeasure):
	"""Average found composition time"""
	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__searchPattern = re.compile('DEBUG .*?  - Peer [0-9]+ started composition search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		self.__foundPattern = re.compile('DEBUG .*?  - Peer [0-9]+ received composition for search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		
		self.__searches = {}
		
	def parseLine(self, line):
		m = self.__searchPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			time = float(m.group(2).replace(',','.'))	
			self.__searches[searchID] = time			
			return
		
		m = self.__foundPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			time = float(m.group(2).replace(',','.'))
			
			if searchID in self.__searches:
				searchTime = self.__searches[searchID]
				elapsedTime = time - searchTime
				self.periodicAvgValues.addValue(elapsedTime, searchTime) 
				del self.__searches[searchID]
				
			return
	