from ParameterPopulator import ParameterPopulator
from CompositionsPopulator import CompositionsPopulator
from ServicePopulator import ServicePopulator

class PopulatorGenerator:
    
    def generatePopulator(self, entries):
        
        self.__populator = ''
        
        for entry in entries:
           value = entry.firstChild.data
           key = entry.getAttribute('key')
           
           if key == 'populator':
               self.__populator = value
                       
        if self.__populator == 'ParameterPopulator':
            return ParameterPopulator(entries)
        if self.__populator == 'CompositionsPopulator':
            return CompositionsPopulator(entries)
        if self.__populator == 'ServicePopulator':
            return ServicePopulator(entries)
        
        return None