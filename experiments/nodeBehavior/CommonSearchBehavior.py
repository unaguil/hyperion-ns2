import math

from time import time

import util.TimeFormatter as TimeFormatter

DELTA_TIME = 0.5

class CommonSearchBehavior:
    """
        Defines the common behavior for periodic actions generation.
    """
    
    def __init__(self, entries, nodePopulator, behaviorName, different=False):
        self.__different = different
        
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "searchFreq":
                self.__searchFreq = float(value)
                
            if key == "finishTime":
                self.__finishTime = float(value)
                
            if key == "nNodes":
                self.__nNodes = int(value)
                
            if key == 'timeRange':
                self.__timeRange = eval(value)
                    
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

    def __getTimeRange(self):
        init, end = self.__timeRange
        
        if init == 'START':
            init = 0.0
            
        if end == 'END' or end >= self.__finishTime:
            end = self.__finishTime
            
        return (init, end)
    
    def generate(self, workingDir, oFile, strBuffer):              
        init, end = self.__getTimeRange()
        
        searches = math.ceil(self.__searchFreq * (self.__getTimeRange()[1] - self.__getTimeRange()[0]))
        
        if self.__different and searches > len(self.getElements()):
            raise Exception('Cannot generated %d searches using %d elements' % (searches, len(self.getElements())))
        
        strBuffer.writeln('')
        strBuffer.writeln('************* %s ****************' % self.__behaviorName)
        strBuffer.writeln('* Nodes: %d' % self.__nNodes)
        strBuffer.writeln('* Frequency: %.3f searches/s' % self.__searchFreq)
        strBuffer.writeln('* Generated: %d searches' % searches)
        strBuffer.writeln('* Time range: [%s, %s] s' % (self.__getTimeRange()[0], self.__getTimeRange()[1]))
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
