import random

from CommonSearchBehavior import CommonSearchBehavior

class CompositionSearchBehavior(CommonSearchBehavior):
    """
        Creates the behavior of the nodes for multicast experimentation.
    """
    def __init__(self, entries, nodePopulator):
        CommonSearchBehavior.__init__(self, entries, nodePopulator, 'Composition search behavior', True)
        
        self.__searchedParameters = {}
        
        self.__availableCompositions = None
        
    def perform(self, time, oFile):
        node = random.randrange(self.getNNodes())
        compositions = self.getElements()
        
        if self.__availableCompositions is None:
            self.__availableCompositions = zip(compositions, range(len(compositions)))
        
        index = random.randrange(len(self.__availableCompositions))
        oFile.write('$ns_ at %f "$agents(%d) agentj composeService %d\"\n' % (time, node, self.__availableCompositions[index][1]))
        del self.__availableCompositions[index] 
         
    def getElements(self):
        return self.getNodePopulator().getCompositions()
        
    def printInfo(self, strBuffer):
        strBuffer.writeln('* Using a total of %d different compositions' % len(self.getNodePopulator().getCompositions()))        