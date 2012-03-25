import re
from measures.periodicValues.PeriodicValues import PeriodicValues
from measures.generic.GenericMeasure import GenericMeasure as GenericMeasure
import measures.generic.Units as Units

class TotalTrafficOverhead(GenericMeasure):
    def __init__(self, period, simulationTime):        
        GenericMeasure.__init__(self, '', period, simulationTime, Units.MESSAGE_TRAFFIC_OVERHEAD)
        
        self.__initializePattern = re.compile('INFO  peer.BasicPeer  - Peer ([0-9]+) initializing ([0-9]+\,[0-9]+).*?')
        self.__sizePattern = re.compile('DEBUG peer.BasicPeer  - Peer [0-9]+ broadcasting .*? ([0-9]+) bytes.*?')
        
        self.__totalSize = 0
        
        self.__nodes = 0
        
    def setPatterns(self, patterns):
        self.__sizePatterns = patterns
        
    def parseLine(self, line):
        m = self.__initializePattern.match(line)
        if m is not None:
            peer = m.group(1)
            time = float(m.group(2).replace(',','.'))
            
            self.__nodes += 1

            return
        
        m = self.__sizePattern.match(line)
        if m is not None:
            size = int(m.group(1))                
            self.__totalSize += size

            return
            
    def getValues(self): 
        return PeriodicValues(0, self.getPeriod(), self.getSimulationTime())

    def getTotalValue(self):
        return self.__totalSize / float(self.__nodes) / self.getSimulationTime() / 1024.0
        
        
        
