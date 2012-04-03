import re

from measures.periodicValues.PeriodicValues import PeriodicValues
from measures.generic.GenericMeasure import GenericMeasure as GenericMeasure

import measures.generic.Units as Units 

class Overhead(GenericMeasure):
    def __init__(self, period, simulationTime):        
        GenericMeasure.__init__(self, '', period, simulationTime, Units.MESSAGE_OVERHEAD)
        
        self.__measures = []
        
        self.__initializePattern = re.compile('INFO  peer.BasicPeer  - Peer ([0-9]+) initializing ([0-9]+\,[0-9]+).*?')        
        self.__neighbors = 0
        
    def addMeasure(self, measure):        
        self.__measures.append(measure)
        
    def parseLine(self, line):
        m = self.__initializePattern.match(line)
        if m is not None:
            self.__neighbors += 1
            return
        
        for measure in self.__measures:
            measure.parseLine(line)
            
    def getValues(self): 
        return PeriodicValues(0, self.getPeriod(), self.getSimulationTime())

    def getTotalValue(self):
        total = 0
        for measure in self.__measures:
            total += measure.getTotalValue()
        return total / float(self.__neighbors) / self.getSimulationTime()
        
        
        
