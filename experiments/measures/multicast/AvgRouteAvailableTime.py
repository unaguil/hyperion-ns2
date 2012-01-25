import re
import numpy

import os.path

import measures.generic.Units as Units
from measures.generic.GenericAvgMeasure import GenericAvgMeasure

class AvgRouteAvailableTime(GenericAvgMeasure):	
	def __init__(self, period, simulationTime):		
		GenericAvgMeasure.__init__(self, period, simulationTime, Units.SECONDS)
		
		self.__addedRoute = re.compile('DEBUG multicast.search.unicastTable.UnicastTable  - Peer ([0-9]+) added route to ([0-9]+) ([0-9]+\,[0-9]+).*?')
		self.__removedRoute = re.compile('DEBUG multicast.search.unicastTable.UnicastTable  - Peer ([0-9]+) removed route to ([0-9]+) ([0-9]+\,[0-9]+).*?')		
		
		self.__addedRoutes = {}

	def parseLine(self, line):		
		m = self.__addedRoute.match(line)
		if m is not None:
			peer = m.group(1)
			dest = m.group(2)
			time = float(m.group(3).replace(',','.')) 
			
			if not (peer, dest) in self.__addedRoutes:
				self.__addedRoutes[peer, dest] = time
				
			return
						   
		m = self.__removedRoute.match(line)
		if m is not None:
			peer = m.group(1)
			dest = m.group(2)
			time = float(m.group(3).replace(',','.')) 
			
			if (peer, dest) in self.__addedRoutes:
				addedTime = self.__addedRoutes[peer, dest]
				
				self.periodicAvgValues.addValue(time - addedTime, foundTime)
				del self.__addedRoutes[peer, dest]
								
			return      
		 
	