import random

from CommonSearchBehavior import CommonSearchBehavior

class SearchBehavior(CommonSearchBehavior):
    """
        Creates the behavior of the nodes for multicast experimentation.
    """
    def __init__(self, entries, nodePopulator):
        CommonSearchBehavior.__init__(self, entries, nodePopulator, 'Search behavior')
        
        self.__activeSearches = []
        
    def perform(self, time, oFile):
        for i in xrange(self.getSimultaneous()):        
            node, parameter = self.__randomSelect()
            self.__activeSearches.append((node, parameter))
            oFile.write('$ns_ at %f \"$agents(%d) agentj searchParameter I-%s\"\n' % (time, node, parameter))
            
    def __randomSelect(self):
        node = random.randrange(self.getNNodes())
        availableElements = list(self.getElements())
        index = random.randrange(len(availableElements))
        parameter = availableElements[index]
        return node, parameter
    
    def getElements(self):
        return self.getNodePopulator().getUsedConcepts()
    
    def printInfo(self, strBuffer):
        strBuffer.writeln('* Using a total of %d concepts' % len(self.getElements()))        