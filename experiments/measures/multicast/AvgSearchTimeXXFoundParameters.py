import re
import numpy

import os.path

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgSearchTimeXXFoundParameters(GenericAvgMeasure):	
	def __init__(self, period, simulationTime, minRatio):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__searchPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer .*? started search for parameters (\[.*?\]) searchID (\(.*?\)) .*? ([0-9]+\,[0-9]+).*?')
		self.__foundPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer ([0-9]+) accepted multicast.search.message.SearchMessage (\(.*?\)) distance .*? parameters (\[.*?\]) ([0-9]+\,[0-9]+).*?')
		
		self.__currentSearches = {}
		self.__startTime = {}
		
		self.__minRatio = minRatio
		
	def start(self, tempDir):
		conceptsFile = os.path.join(tempDir, 'parameters', 'usedConcepts.txt')
		try:
			file = open(conceptsFile, 'r')
			self.__availableParameters = eval(file.readline())
			file.close()
		except IOError:
			print 'Could not open file %s' % conceptsFile
	
	def __getParameters(self, str):
		return [str.strip() for str in str[1:-1].split(',')]

	def parseLine(self, line):
		m = self.__searchPattern.match(line)
		if m is not None:
			parameters = self.__getParameters(m.group(1))
			searchID = m.group(2)
			time = float(m.group(3).replace(',','.'))	
			
			self.__currentSearches[searchID] = {}
			self.__startTime[searchID] = time
				
			return
		
		m = self.__foundPattern.match(line)
		if m is not None:
			peer = m.group(1)
			searchID = m.group(2)
			parameters = self.__getParameters(m.group(3))
			time = float(m.group(4).replace(',','.'))
			
			if searchID in self.__currentSearches:
				for parameter in parameters:
					if not parameter in self.__currentSearches[searchID]:
						self.__currentSearches[searchID][parameter] = []
					if peer not in self.__currentSearches[searchID][parameter]:
						self.__currentSearches[searchID][parameter].append(peer)
						
				if self.__calculateFoundParametersRatio(searchID) >= self.__minRatio:
					startTime = self.__startTime[searchID] 
					self.periodicAvgValues.addValue(time - startTime, startTime)
					del self.__startTime[searchID]
					del self.__currentSearches[searchID]
			
			return 
		
	def __getLostParameters(self, str):
		parameters = []
		strings = str.split(', (')
		for s in strings:
			values = s.split('=')[1] 
			parameters.extend(self.__getParameters(values))
		return parameters
				
	def __calculateFoundParametersRatio(self, searchID):
		foundParameters = self.__currentSearches[searchID]
		ratios = []
		for foundParameter, peers in foundParameters.iteritems():
			ratio = len(peers) / float(self.__availableParameters[foundParameter.split('-')[1]])
			ratios.append(ratio)
				
		if len(ratios) == 0:
			return 0.0
		else:
			return numpy.mean(ratios) 
			
	def __checkParameter(self, parameter, list):
		if not parameter in list:
			list[parameter] = 0 
	
