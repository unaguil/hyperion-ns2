import os

from xml.dom import minidom

from Taxonomy import Taxonomy

import random

class IncorrectSolution(Exception):
    def __init__(self):
        pass

def count(l):
	counter = {}
	for e in l:
		if not e in counter:
			counter[e] = 1
		else:
			counter[e] += 1
	return counter

class ServicePopulator:
    def __init__(self, entries):
        self.__replicateServices = 1
        
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "nNodes":
                self.__nNodes = int(value)
            if key == "services":
                self.__services = int(value)
            if key == 'serviceParameters':
                self.__serviceParameters = int(value)
            if key == "replicateServices":
                self.__replicateServices = int(value)
                
    def getUsedConcepts(self):
        return self.__usedConcepts.keys()
    
    def generate(self, workingDir, strBuffer):            
        strBuffer.writeln('')
        strBuffer.writeln('************* Service populator ****************')
        nodeTable, taxonomy, usedConcepts = self.__generate(self.__nNodes, self.__services, self.__serviceParameters, self.__replicateServices, strBuffer)
        
        dir = os.path.join(workingDir, 'parameters')
        
        strBuffer.writeln('* Creating %s directory ' % dir)
        os.mkdir(dir)    
        
        self.__generateXMLNodeConfigurations(dir, nodeTable, strBuffer)
        
        self.__saveGeneratedParameters(dir, usedConcepts)
        
        self.__usedConcepts = usedConcepts
        
        self.__writeTaxonomy(workingDir, taxonomy)

        strBuffer.writeln('**************************************************')
        
    def __generate(self, nNodes, numServices, serviceParameters, replicateServices, strBuffer):                                    
        services, taxonomy = self.__generateServices(numServices, serviceParameters)        
        
        nodesWithServices = len(services) * replicateServices
        selectedNodes = random.sample(range(nNodes), nodesWithServices) 
                
        replicatedServices = []
        for service in services:
            replicatedServices += [service] * replicateServices
        
        nodeTable = {}
        for node, service in zip(selectedNodes, replicatedServices):
            nodeTable[node] = service
                
        usedConcepts = {}
        for parameter in self.__getParameters(nodeTable):
            for concept in taxonomy.getParents(parameter):
                if concept not in usedConcepts:
                    usedConcepts[concept] = 0
                usedConcepts[concept] += 1
                
        strBuffer.writeln('* Services: %.d' % numServices)
        strBuffer.writeln('* Service parameters: %d' % serviceParameters)
        strBuffer.writeln('* Replicate numServices: %d' % replicateServices)
        strBuffer.writeln('* Nodes with services: %d' % len(nodeTable))
        strBuffer.writeln('* Total generated parameters: %d' % self.__countParameters(nodeTable))
        
        return nodeTable, taxonomy, usedConcepts
    
    def __generateServices(self, numServices, serviceParameters):
        generator = self.__parameterGenerator()
        
        services = []
        taxonomy = Taxonomy('Root')
        for i in xrange(numServices):
            service = []
            for i in xrange(serviceParameters):
                p = generator.next()
                service.append(p)
                taxonomy.addChild('Root', p)
            services.append(service)
        return services, taxonomy
    
    def __countParameters(self, nodeTable): 
        numParameters = 0
        for parameters in nodeTable.values():
            numParameters += len(parameters)
        return numParameters
    
    def __getParameters(self, nodeTable): 
        allParameters = []
        for parameters in nodeTable.values():
            allParameters += parameters
        return allParameters
                            
    def __parameterGenerator(self):
        currentParameter = 0
        while True:
            yield '%d' % currentParameter
            currentParameter += 1 
            
    def __generateXML(self, node, parameters, outputFilePath):
        doc = minidom.Document()
        
        parameterList = doc.createElement('parameterlist')
        doc.appendChild(parameterList)          
        
        for p in parameters:
            parameter = doc.createElement('parameter')
            parameter.setAttribute('id', 'I-' + p)
            parameterList.appendChild(parameter)
        
        oFile = open(outputFilePath, 'w')
        oFile.write(doc.toprettyxml())
        oFile.close()
        
    def __writeTaxonomy(self, dir, taxonomy):
        taxonomyFilePath = os.path.join(dir, 'taxonomy.xml')
        oFile = open(taxonomyFilePath, 'w')
        xmlTaxonomy = taxonomy.createXMLDocument() 
        oFile.write(xmlTaxonomy.toprettyxml())
        oFile.close()
        
    def __generateXMLNodeConfigurations(self, outputDir, parametersTable, strBuffer):                        
        for node in parametersTable.keys():
            if len(parametersTable[node]) > 0:
                filePath = os.path.join(outputDir, 'Parameters' + str(node) + '.xml')
                self.__generateXML(node, set(parametersTable[node]), filePath)
                
    def __saveGeneratedParameters(self, outputDir, usedConcepts):
         filePath = os.path.join(outputDir, 'usedConcepts.txt')
         file = open(filePath, 'w')
         file.write(str(usedConcepts))    
         file.close()
        
