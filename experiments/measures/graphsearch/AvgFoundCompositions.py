import re
import numpy

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

import measures.generic.Units as Units

class AvgFoundCompositions(GenericAvgMeasure):
	"""Average found compositions"""
	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.COMPOSITIONS)
		
		self.__searchPattern = re.compile('DEBUG graphsearch.Peer  - Peer [0-9]+ started composition search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		self.__foundPattern = re.compile('DEBUG graphsearch.Peer  - Peer [0-9]+ received composition for search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		
		self.__searches = {}
		
	def parseLine(self, line):
		m = self.__searchPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			time = float(m.group(2).replace(',','.'))
			
			self.__searches[searchID] = False
			
			self.periodicAvgValues.addValue(self.__calculateAvgFoundCompositions(), time)
				
			return
		
		m = self.__foundPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			time = float(m.group(2).replace(',','.'))
			
			self.__searches[searchID] = True
								
			self.periodicAvgValues.addValue(self.__calculateAvgFoundCompositions(), time)
			
			return 
				
	def __calculateAvgFoundCompositions(self):			
		if len(self.__searches) == 0:
			return 0.0
		
		found = 0
		
		for searchID in self.__searches.keys():
			if self.__searches[searchID]:
				found +=1
				
		return found / len(self.__searches)		
	