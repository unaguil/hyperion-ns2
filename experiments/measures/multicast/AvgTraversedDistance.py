import re
import numpy

import os.path

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgTraversedDistance(GenericAvgMeasure):	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.HOPS)
		
		self.__acceptedPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer [0-9]+ accepted multicast.search.message.SearchMessage .*? distance ([0-9]+) .*? ([0-9]+\,[0-9]+).*?')
		self.__foundPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? found parameters .*? in node [0-9]+ searchID .*? distance ([0-9]+) ([0-9]+\,[0-9]+).*?')			
	
	def parseLine(self, line):
		m = self.__acceptedPattern.match(line)
		if m is not None:
			distance = int(m.group(1))
			time = float(m.group(2).replace(',','.'))	
			
			self.periodicAvgValues.addValue(distance, time)
				
			return
		
		m = self.__foundPattern.match(line)
		if m is not None:
			distance = int(m.group(1))
			time = float(m.group(2).replace(',','.'))
			
			self.periodicAvgValues.addValue(distance, time)
			
			return 	