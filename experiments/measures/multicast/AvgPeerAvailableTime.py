import re
import numpy

import os.path

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgPeerAvailableTime(GenericAvgMeasure):	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.PARAMETERS)
		
		self.__foundPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer ([0-9]+) found parameters .*? in node ([0-9]+) .*? ([0-9]+\,[0-9]+).*?')
		self.__lostPattern = re.compile('DEBUG multicast.search.ParameterSearchImpl  - Peer ([0-9]+) lost route to destinations (\[.*?\]) ([0-9]+\,[0-9]+).*?')		
		
		self.__foundPeers = {}
	
	def __getParameters(self, str):
		return [str.strip() for str in str[1:-1].split(',')]

	def parseLine(self, line):		
		m = self.__foundPattern.match(line)
		if m is not None:
			searchingPeer = m.group(1)
			sourcePeer = m.group(2)
			time = float(m.group(3).replace(',','.')) 
            
			if not searchingPeer in self.__foundPeers:
				self.__foundPeers[searchingPeer] = {}
			if not sourcePeer in self.__foundPeers[searchingPeer]:
				self.__foundPeers[searchingPeer][sourcePeer] = time
				
			return
						   
		m = self.__lostPattern.match(line)
		if m is not None:
			searchingPeer = m.group(1)
			lostDestinations = eval(m.group(2))
			time = float(m.group(3).replace(',','.')) 
			
			if searchingPeer in self.__foundPeers:
				for lostDestination in lostDestinations:
					if lostDestination in self.__foundPeers[searchingPeer]:
						foundTime = self.__foundPeers[searchingPeer][lostDestination]
						self.periodicAvgValues.addValue(time - foundTime, foundTime)
						del self.__foundPeers[searchingPeer][lostDestination]
				
			return      
		 
	