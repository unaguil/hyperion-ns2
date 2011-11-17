import random

from CommonSearchBehavior import CommonSearchBehavior

class SearchBehavior(CommonSearchBehavior):
    """
        Creates the behavior of the nodes for multicast experimentation.
    """
    def __init__(self, entries, nodePopulator):
        CommonSearchBehavior.__init__(self, entries, nodePopulator, 'Search behavior')
        
        self.__searchedParameters = {}
        
    def perform(self, time, oFile):
        if len(self.getElements()) > 0 and self.getNNodes() > 0:
            node, parameter = self.__randomSelect()
            if not node in self.__searchedParameters:
                self.__searchedParameters[node] = []
                    
            while parameter in self.__searchedParameters[node]:
                node, parameter = self.__randomSelect()
                if not node in self.__searchedParameters:
                    self.__searchedParameters[node] = []
            
            self.__searchedParameters[node].append(parameter) 
            
            oFile.write('$ns_ at %f \"$agents(%d) agentj searchParameter I-%s\"\n' % (time, node, parameter))
            
    def __randomSelect(self):
        node = random.randrange(self.getNNodes())
        parameter = str(random.randrange(len(self.getNodePopulator().getParameters())))
        return node, parameter
    
    def getElements(self):
        return self.getNodePopulator().getParameters()
    
    def printInfo(self, strBuffer):
        strBuffer.writeln('* %s: Using a total of %d different parameters' % (self.getBehaviorName(), len(self.getNodePopulator().getParameters())))        