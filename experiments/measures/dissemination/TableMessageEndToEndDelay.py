from measures.generic.GenericMeasure import GenericMeasure
import re

import measures.generic.Units as Units

class TableMessageEndToEndDelay(GenericMeasure):    
    
    def __init__(self, period, simulationTime):    
        GenericMeasure.__init__(self, '', period, simulationTime, Units.SECONDS)
        self.__receivedPattern = re.compile(r"DEBUG peer.BasicPeer  - .*? received dissemination.newProtocol.message.TableMessage .*? ([0-9]+\,[0-9]+).*?") 
        self.__sentPattern = re.compile(r"DEBUG peer.BasicPeer  - .*? sending dissemination.newProtocol.message.TableMessage .*? ([0-9]+\,[0-9]+).*?")
        
        self.__firstTimeSent = None
        self.__lastTimeReceived = None
        
    def parseLine(self, line):
        if self.__firstTimeSent is None:
            m = self.__sentPattern.match(line)
            if m is not None: 
                self.__firstTimeSent = float(m.group(1).replace(',','.'))
                         
        m = self.__receivedPattern.match(line)
        if m is not None:
            self.__lastTimeReceived = float(m.group(1).replace(',','.'))
            
    def getTotalValue(self):
        if self.__firstTimeSent is not None and self.__lastTimeReceived is not None:
            return self.__lastTimeReceived - self.__firstTimeSent
        else:
            return 0.0
    
    def isDiscardable(self):
        return False
