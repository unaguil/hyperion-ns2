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
        if len(self.getElements()) > 0:
            for i in xrange(self.getSimultaneous()):
                validSearch = self.selectSearchType()
                if validSearch:         
                    node, parameter = self.__randomSelect()
                else:
                    node, parameter = self.__createInvalidSearch()
                    
                self.__activeSearches.append((node, parameter, time))
                oFile.write('$ns_ at %f \"$agents(%d) agentj searchParameterGeneric I-%s\"\n' % (time, node, parameter))
                
    def finishSearches(self, searchDuration, oFile):
        for node, parameter, time in self.__activeSearches:
            cancelTime = time + searchDuration
            oFile.write('$ns_ at %f \"$agents(%d) agentj cancelSearch I-%s\"\n' % (cancelTime, node, parameter))
            
    def __randomSelect(self):
        node = random.randrange(self.getNNodes())
        availableElements = self.getElements()        
        index = random.randrange(len(availableElements))
        parameter = availableElements[index]
        return node, parameter
    
    def __createInvalidSearch(self):
        node = random.randrange(self.getNNodes())
        return node, '#'
    
    def getElements(self):
        return list(self.getNodePopulator().getUsedConcepts())
    
    def printInfo(self, strBuffer):
        strBuffer.writeln('* Using a total of %d concepts' % len(self.getElements()))        