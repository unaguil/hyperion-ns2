import random

from CommonSearchBehavior import CommonSearchBehavior

class CompositionSearchBehavior(CommonSearchBehavior):
    """
        Creates the behavior of the nodes for multicast experimentation.
    """
    def __init__(self, entries, nodePopulator):
        CommonSearchBehavior.__init__(self, entries, nodePopulator, 'Composition search behavior')
        
        self.__searchedParameters = {}
        
        self.__availableCompositions = None
        
        self.__compositionTable = {}
        
    def perform(self, time, oFile):
        compositions = self.getElements()
        if compositions:
            if self.mustBeDifferent():
                if self.__availableCompositions is None:
                    self.__availableCompositions = zip(compositions, range(len(compositions)))
                
                index = random.randrange(len(self.__availableCompositions))
                compositionIndex = self.__availableCompositions[index][1]
                del self.__availableCompositions[index]
            else:
                compositionIndex = random.randrange(len(compositions))
            
            if not compositionIndex in self.__compositionTable:
                node = random.randrange(self.getNNodes())
                self.__compositionTable[compositionIndex] = [node]
            else:
                nodes = range(self.getNNodes())
                node = random.choice(nodes)
                self.__compositionTable[compositionIndex].append(node)
                         
            oFile.write('$ns_ at %f "$agents(%d) agentj composeService %d\"\n' % (time, node, compositionIndex))
         
    def getElements(self):
        return self.getNodePopulator().getCompositions()
        
    def printInfo(self, strBuffer):
        if self.mustBeDifferent():
            strBuffer.writeln('* Using a total of %d *different* compositions' % len(self.getNodePopulator().getCompositions()))
        else:
            strBuffer.writeln('* Using a total of %d compositions' % len(self.getNodePopulator().getCompositions()))
