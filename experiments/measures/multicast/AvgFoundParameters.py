import re
import numpy

import os.path

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgFoundParameters(GenericAvgMeasure):	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.RATIO)
		
		self.__searchPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? started search for parameters (\[.*?\]) searchID (\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')
		self.__foundPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? found parameters (\[.*?\]) in node ([0-9]+) searchID (\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')
		
		self.__currentSearches = {}
		
	def start(self, tempDir):
		conceptsFile = os.path.join(tempDir, 'parameters', 'usedConcepts.txt')
		file = open(conceptsFile, 'r')
		self.__availableParameters = eval(file.readline())
		file.close()
	
	def __getParameters(self, str):
		return [str.strip() for str in str[1:-1].split(',')]

	def parseLine(self, line):
		m = self.__searchPattern.match(line)
		if m is not None:
			parameters = self.__getParameters(m.group(1))
			searchID = m.group(2)
			time = float(m.group(3).replace(',','.'))	
			
			self.__currentSearches[searchID] = {}
			
			self.periodicAvgValues.addValue(self.__calculateAvgFoundParameters(), time)
				
			return
		
		m = self.__foundPattern.match(line)
		if m is not None:
			parameters = self.__getParameters(m.group(1))
			peer = m.group(2)
			searchID = m.group(3)
			time = float(m.group(4).replace(',','.'))
			
			for parameter in parameters:
				if not parameter in self.__currentSearches[searchID]:
					self.__currentSearches[searchID][parameter] = []
				if peer not in self.__currentSearches[searchID][parameter]:
					self.__currentSearches[searchID][parameter].append(peer) 
								
			self.periodicAvgValues.addValue(self.__calculateAvgFoundParameters(), time)
			
			return 
		
	def __getLostParameters(self, str):
		parameters = []
		strings = str.split(', (')
		for s in strings:
			values = s.split('=')[1] 
			parameters.extend(self.__getParameters(values))
		return parameters
				
	def __calculateAvgFoundParameters(self):			
		avgRatios = []

		for foundParameters in self.__currentSearches.values():
			for foundParameter, peers in foundParameters.iteritems():
				ratio = len(peers) / float(self.__availableParameters[foundParameter.split('-')[1]])
				avgRatios.append(ratio)
				
		if len(avgRatios) == 0:
			return 0.0
		else:
			return numpy.mean(avgRatios) 
			
	def getTotalValue(self):
		return self.__calculateAvgFoundParameters()
			
	def __checkParameter(self, parameter, list):
		if not parameter in list:
			list[parameter] = 0 
	