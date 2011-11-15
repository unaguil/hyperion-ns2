from measures.periodicValues.PeriodicAvgValues import PeriodicAvgValues
from Measure import Measure

class GenericAvgMeasure(Measure):
    def __init__(self, period, simulationTime, units, maintainLastValue=False):
        Measure.__init__(self, period, simulationTime, units)
        
        self.periodicAvgValues = PeriodicAvgValues(period, simulationTime, maintainLastValue)
        
        self.__units = units
        
    def getTotalValue(self):
        return self.periodicAvgValues.getAvgTotal()
    
    def getValues(self): 
        return self.periodicAvgValues.getPeriodicValues()