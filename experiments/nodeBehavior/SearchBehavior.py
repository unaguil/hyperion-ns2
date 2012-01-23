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
        parameter = str(random.randrange(len(self.getElements())))
        return node, parameter
    
    def getElements(self):
        return self.getNodePopulator().getTaxonomy().getAllConcepts()
    
    def printInfo(self, strBuffer):
        strBuffer.writeln('* %s: Using a total of %d parameters' % (self.getBehaviorName(), len(self.getElements())))        