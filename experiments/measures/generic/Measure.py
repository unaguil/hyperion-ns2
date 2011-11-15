
class Measure:
    def __init__(self, period, simulationTime, units): 
        self.__period = period
        self.__simulationTime = simulationTime
        self.__units = units
    
    def getName(self):
        return self.__class__.__name__
    
    def getType(self):
        clazz = str(self.__class__)
        return clazz[:clazz.rfind('.')]
    
    def getPeriod(self):
        return self.__period
    
    def getSimulationTime(self):
        return self.__simulationTime
    
    def getUnits(self):
        return self.__units
    
    def finish(self):
        pass