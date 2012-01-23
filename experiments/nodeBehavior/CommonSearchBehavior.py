import math

from time import time

import util.TimeFormatter as TimeFormatter
import util.SimTimeRange as SimTimeRange

DELTA_TIME = 0.5

class CommonSearchBehavior:
    """
        Defines the common behavior for periodic actions generation.
    """
    
    def __init__(self, entries, nodePopulator, behaviorName):
        self.__different = False
        
        self.__simultaneous = 0
        self.__different = False
                
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "searchFreq":
                self.__searchFreq = float(value)
                
            if key == "finishTime":
                self.__finishTime = float(value)
                
            if key == "discardTime":
                self.__discardTime = float(value)
                
            if key == "nNodes":
                self.__nNodes = int(value)
                
            if key == 'timeRange':
                self.__timeRange = eval(value)
                
            if key == 'different':
                self.__different = eval(value)
                
            if key == 'simultaneous':
                self.__simultaneous = float(value)
                    
        self.__nodePopulator = nodePopulator
        
        self.__behaviorName = behaviorName
        
        if self.__searchFreq == 0:
            self.__searchPeriod = 0.0
        else:
            self.__searchPeriod = 1 / self.__searchFreq            
            
    def getNNodes(self):
        return self.__nNodes
    
    def getNodePopulator(self):
        return self.__nodePopulator
    
    def getBehaviorName(self):
        return self.__behaviorName
    
    def mustBeDifferent(self):
        return self.__different
    
    def generate(self, workingDir, oFile, strBuffer):              
        init, end = SimTimeRange.getTimeRange(self.__timeRange, self.__finishTime, self.__discardTime)
        searches = int(math.ceil(self.__searchFreq * (end - init)))
        
        if self.__different and searches > len(self.getElements()):
            raise Exception('Cannot generated %d searches using %d elements' % (searches, len(self.getElements())))
        
        strBuffer.writeln('')
        strBuffer.writeln('************* %s ****************' % self.__behaviorName)
        strBuffer.writeln('* Frequency: %.1f searches/s' % self.__searchFreq)
        strBuffer.writeln('* Generated: %d searches' % searches)
        strBuffer.writeln('* Time range: [%s, %s] s' % (init, end))
        strBuffer.writeln("* Simultaneous searches: %.2f" % (self.getSimultaneous()))
        self.printInfo(strBuffer)

        startTime = time()
        
        if self.__searchPeriod > 0.0:            
            #Create search events each specified period of time during specified time range        
            currentTime = init + DELTA_TIME
            while (currentTime < end + DELTA_TIME):
                #perform action
                self.perform(currentTime, oFile)
                
                #Increment time
                currentTime += self.__searchPeriod
                
        strBuffer.writeln('* Behavior generation time: %s ' % TimeFormatter.formatTime(time() - startTime)) 
        strBuffer.writeln('**********************************************************')
                
    def perform(self, time, oFile):
        pass 
    
    def printInfo(self, strBuffer):
        pass
    
    def getElements(self):
        pass
    
    def getSimultaneous(self):
        if self.__simultaneous == 0:
            return 1
        else:
            return int(self.__simultaneous * self.getNNodes())
