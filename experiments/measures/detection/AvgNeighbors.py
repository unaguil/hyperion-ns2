import re
import numpy

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgNeighbors(GenericAvgMeasure):
	"""Average neighbors for a node"""
	
	def __init__(self, period, simulationTime):
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.NEIGHBORS, maintainLastValue=True)
		
		self.__initializePattern = re.compile('INFO  peer.BasicPeer  - Peer ([0-9]+) initializing ([0-9]+\,[0-9]+).*?')
		self.__appearPattern = re.compile('DEBUG detection.beaconDetector.BeaconDetector  - Peer ([0-9]+) has new neighbors: (\[.*?\]) ([0-9]+\,[0-9]+).*?')
		self.__disappearPattern = re.compile('DEBUG detection.beaconDetector.BeaconDetector  - Peer ([0-9]+) has lost neighbors: (\[.*?\]) ([0-9]+\,[0-9]+).*?')
		
		self.__currentNeighbors = {}

	def parseLine(self, line):
		m = self.__initializePattern.match(line)
		if m is not None:
			peer = m.group(1)
			time = float(m.group(2).replace(',','.'))
			
			self.__currentNeighbors[peer] = []

			self.periodicAvgValues.addValue(self.__avgNeighbors(), time)

			return
					
		m = self.__appearPattern.match(line)
		if m is not None:
			peer = m.group(1)
			neighbors = eval(m.group(2))
			time = float(m.group(3).replace(',','.'))
			
			self.__currentNeighbors[peer] += neighbors
			
			self.periodicAvgValues.addValue(self.__avgNeighbors(), time)
			
			return 
		
		m = self.__disappearPattern.match(line) 
		if m is not None:
			peer = m.group(1)
			neighbors = eval(m.group(2))
			time = float(m.group(3).replace(',','.'))
			
			for neighbor in neighbors:
				self.__currentNeighbors[peer].remove(neighbor)
				
			self.periodicAvgValues.addValue(self.__avgNeighbors(), time)
			
	def __avgNeighbors(self):
		lenghts = [len(neighbors) for neighbors in self.__currentNeighbors.values()]
		return numpy.mean(lenghts)			
			
	def isDiscardable(self):
		return False
