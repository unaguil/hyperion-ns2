from SearchBehavior import SearchBehavior
from CompositionSearchBehavior import CompositionSearchBehavior

import sys

class NodeBehaviorGenerator:
    
    def generateNodeBehavior(self, entries, nodePopulator):
        
        self.__nodeBehavior = ''
        
        for entry in entries:
           value = entry.firstChild.data
           key = entry.getAttribute('key')
           
           if key == 'nodeBehavior':
               self.__nodeBehavior = value
                       
        if self.__nodeBehavior == 'SearchBehavior':
            return SearchBehavior(entries, nodePopulator)
        if self.__nodeBehavior == 'CompositionSearchBehavior':
            return CompositionSearchBehavior(entries, nodePopulator)
        
        print 'Invalid node behavior %s' % self.__nodeBehavior
        sys.exit()