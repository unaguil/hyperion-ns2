import re
from measures.periodicValues.PeriodicValues import PeriodicValues

from Measure import Measure

class GenericMeasure(Measure):
    def __init__(self, pattern, period, simulationTime, units):
        Measure.__init__(self, period, simulationTime, units)
                
        self.__periodicValues = PeriodicValues(0, period, simulationTime)
        
        self.__prog = re.compile(pattern)
        
        self.__units = units
    
    def getTotalValue(self):
        return self.__periodicValues.getTotal()
    
    def incValue(self, time, simulationTime):
        self.__periodicValues.incValue(time, self.getPeriod(), simulationTime)
        
    def parseInc(self, line):
        m = self.__prog.match(line)
        if m is not None:
            time  = float(m.group(1).replace(',','.'))
            self.incValue(time, self.getSimulationTime())
            
    def getProg(self):
        return self.__prog 
    
    def getValues(self): 
        return self.__periodicValues