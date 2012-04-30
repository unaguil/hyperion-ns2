import random

from CommonSearchBehavior import CommonSearchBehavior

class CompositionSearchBehavior(CommonSearchBehavior):
    """
        Creates the behavior of the nodes for multicast experimentation.
    """
    def __init__(self, entries, nodePopulator):
        CommonSearchBehavior.__init__(self, entries, nodePopulator, 'Composition search behavior')
        
        self.__firstTime = True
        
        self.__nodeTable = {}
        
    def perform(self, time, oFile):
        if self.__firstTime:
            selectedNodes = random.sample(range(self.getNNodes()), len(self.getElements()))
            
            for node, compositionIndex in zip(selectedNodes, range(len(self.getElements()))):
                oFile.write('$ns_ at %f "$agents(%d) agentj prepareComposition %d\"\n' % (1.0, node, compositionIndex))
                if not node in self.__nodeTable:
                    self.__nodeTable[node] = []
                self.__nodeTable[node].append(compositionIndex)
                
            self.__firstTime = False
            
        node = random.choice(self.__nodeTable.keys())
        compositionIndex = random.choice(self.__nodeTable[node])                        
        oFile.write('$ns_ at %f "$agents(%d) agentj composeService %d\"\n' % (time, node, compositionIndex))
         
    def getElements(self):
        return self.getNodePopulator().getCompositions()
        
    def printInfo(self, strBuffer):
        if self.mustBeDifferent():
            strBuffer.writeln('* Using a total of %d *different* compositions' % len(self.getNodePopulator().getCompositions()))
        else:
            strBuffer.writeln('* Using a total of %d compositions' % len(self.getNodePopulator().getCompositions()))
