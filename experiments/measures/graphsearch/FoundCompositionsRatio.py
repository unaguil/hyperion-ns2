import re
import numpy

import measures.generic.Units as Units
from measures.generic.GenericMeasure import GenericMeasure
from measures.periodicValues.PeriodicValues import PeriodicValues

class FoundCompositionsRatio(GenericMeasure):
	"""Ratio of found compositions"""
	
	def __init__(self, period, simulationTime):		
		GenericMeasure.__init__(self, '', period, simulationTime, Units.RATIO)
		
		self.__searchPattern = re.compile('DEBUG .*?  - Peer [0-9]+ started composition search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		self.__foundPattern = re.compile('DEBUG .*?  - Peer [0-9]+ received composition for search (\(.*?\)).*?([0-9]+\,[0-9]+).*?')
		
		self.__searches = {}
		
	def parseLine(self, line):
		m = self.__searchPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			startTime = float(m.group(2).replace(',','.'))
			self.__searches[searchID] = (False, startTime)
			return
		
		m = self.__foundPattern.match(line)
		if m is not None:
			searchID = m.group(1)
			self.__searches[searchID] = (True, self.__searches[searchID][1])  
			return
		
	def getTotalValue(self):
		if len(self.__searches) == 0:
			return 0.0
		else:
			founds = len([found for found, time in self.__searches.values() if found])
			return founds / float(len(self.__searches))
		
	def getValues(self):
		values = PeriodicValues(0, self.getPeriod(), self.getSimulationTime())
		
		searches = GenericMeasure('', self.getPeriod(), self.getSimulationTime(), Units.SEARCHES)
		founds = GenericMeasure('', self.getPeriod(), self.getSimulationTime(), Units.COMPOSITIONS)
		
		for found, startTime in self.__searches.values():
			searches.incValue(startTime, self.getSimulationTime())
			if found:
				founds.incValue(startTime, self.getSimulationTime())
				
		searchesArray = searches.getValues()
		foundsArray = founds.getValues()
		
		for index in xrange(len(searchesArray)):
			search = searchesArray.getValue(index)
			found = foundsArray.getValue(index)
			if search == 0:
				values.setValue(index, 0);
			else:
				values.setValue(index, found / float(search))
			 
		return values
	