from measures.periodicValues.PeriodicAvgValues import PeriodicAvgValues

class GenericAvgMeasure:
    def __init__(self, period, simulationTime, units, maintainLastValue=False):
        self.periodicAvgValues = PeriodicAvgValues(period, simulationTime, maintainLastValue)
        
        self.__units = units
        
    def getType(self):
        return self.__class__.__name__
    
    def getPeriod(self):
        return self.periodicAvgValues.getPeriod()
    
    def getSimulationTime(self):
        return self.periodicAvgValues.getSimulationTime()
    
    def getTotalValue(self):
        return self.periodicAvgValues.getAvgTotal()
    
    def getValues(self): 
        return self.periodicAvgValues.getPeriodicValues()
    
    def getUnits(self):
        return self.__units
    
    def finish(self):
        pass