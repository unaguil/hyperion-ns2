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

class ParameterPopulator:
    """Provides functions to populate a the list of parameters for a set of nodes
       It also includes a function to generate the XML configuration for each node in the format used in simulations.
    """
    def __init__(self, entries):
        self.__equalityDistribution = {}
        
        self.__usedConcepts = {}
        
        self.__repeatParameters = 0.0
        
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "nNodes":
                self.__nNodes = int(value)
            if key == "nDistribution":
                self.__nDistribution = float(value)
            if key == "parametersPerNode":
                self.__parametersPerNode = int(value)
            if key == 'equalityDistribution':
                self.__equalityDistribution = eval(value)
            if key == 'repeatParameters':
                self.__repeatParameters = float(value)
    
    def generate(self, workingDir, strBuffer):            
        strBuffer.writeln('')
        strBuffer.writeln('************* Parameter populator ****************')
        parametersTable, taxonomy = self.__generate(self.__nNodes, self.__nDistribution, self.__parametersPerNode, self.__equalityDistribution, self.__repeatParameters, strBuffer)
        
        dir = os.path.join(workingDir, 'parameters')
        
        strBuffer.writeln('* Creating %s directory ' % dir)
        os.mkdir(dir)    
        
        self.__generateXMLNodeConfigurations(dir, parametersTable, strBuffer)
        
        self.__saveGeneratedParameters(dir, self.__usedConcepts)
        
        self.__writeTaxonomy(workingDir, taxonomy)

        strBuffer.writeln('**************************************************')
        
    def getUsedConcepts(self):
        return self.__usedConcepts.keys()
    
    def __normalizeEqualityDistribution(self, equalityDistribution, repeatParameters):
        for key in equalityDistribution.keys():
            equalityDistribution[key] = equalityDistribution[key] * repeatParameters;
    
    def __generate(self, nNodes, nDistribution, parametersPerNode, equalityDistribution, repeatParameters, strBuffer):
        nodesWithParameters = int(nNodes * nDistribution)
                    
        strBuffer.writeln('* Node distribution: %.2f' % nDistribution)
        strBuffer.writeln('* Nodes with parameters: %d' % nodesWithParameters)
        strBuffer.writeln('* Parameters per node: %d' % parametersPerNode)
        
        if repeatParameters > 0.0 and len(equalityDistribution) > 0:
            strBuffer.writeln('* Repeated parameters: %.2f' % repeatParameters)
            strBuffer.writeln('* Using an equality distribution of %s' % str(equalityDistribution))
            self.__normalizeEqualityDistribution(equalityDistribution, repeatParameters) 
            strBuffer.writeln('* Normalized equality distribution %s' % str(equalityDistribution))
        
        nodeTable, taxonomy = self.__distributeParameters(nNodes, equalityDistribution, nodesWithParameters, parametersPerNode)
        
        strBuffer.writeln('* Total generated parameters: %d' % self.__countParameters(nodeTable))
        
        return nodeTable, taxonomy
    
    def __countParameters(self, nodeTable): 
        numParameters = 0
        for parameters in nodeTable.values():
            numParameters += len(parameters)
        return numParameters
    
    def __distributeDifferent(self, nodeTable, generatedParameters, parametersPerNode):
        for node in nodeTable.keys():
            remainingParameters = parametersPerNode - len(nodeTable[node])
            selectedParameters = generatedParameters[:remainingParameters]
            del generatedParameters[:remainingParameters]
            nodeTable[node] += selectedParameters
        return nodeTable; 
                        
    def __parameterGenerator(self):
        currentParameter = 0
        while True:
            yield '%d' % currentParameter
            currentParameter += 1
            
    def __createNodeTable(self, nNodes, nodesWithParameters):
        availableNodes = range(nNodes) 
        nodeTable = {}
        while len(nodeTable) < nodesWithParameters:
            index = random.randrange(len(availableNodes))
            node = availableNodes[index]
            nodeTable[node] = set([])
            del availableNodes[index]
        return nodeTable;
        
    def __distributeParameters(self, nNodes, equalityDistribution, nodesWithParameters, parametersPerNode):
        nodeTable = self.__createNodeTable(nNodes, nodesWithParameters)
        
        generator = self.__parameterGenerator()
        
        taxonomy = self.__createDistributionTaxonomy()
        
        parameters = []
            
        for type, ratio in equalityDistribution.iteritems():
            numParameters = int(ratio * nodesWithParameters * parametersPerNode)
            parameters += [type] * numParameters
            
        generatedParameters = self.__countParameters(nodeTable) 
            
        remainingParameters = nodesWithParameters * parametersPerNode - generatedParameters
        for i in xrange(remainingParameters):
            p = generator.next()
            parameters.append(p)
            taxonomy.addChild('Root', p)
            
        random.shuffle(parameters)
        
        for node in nodeTable.keys():
            selectedParameters = parameters[:parametersPerNode]
            del parameters[:parametersPerNode]
            for p in selectedParameters:
                nodeTable[node].add(p)
            
        distributedParameters = []
        for parameters in nodeTable.values():
            distributedParameters += parameters
        
        for parameter in distributedParameters:
            for concept in taxonomy.getParents(parameter):
                if concept not in self.__usedConcepts:
                    self.__usedConcepts[concept] = 0
                self.__usedConcepts[concept] += 1
                                
        return nodeTable, taxonomy
    
    def __createDistributionTaxonomy(self):
        taxonomy = Taxonomy('Root')
        
        taxonomy.addChild('Root', 'A')
        taxonomy.addChild('Root', 'B')
        taxonomy.addChild('A', 'C')
        taxonomy.addChild('A', 'D')
        taxonomy.addChild('B', 'E')
        taxonomy.addChild('B', 'F')
        taxonomy.addChild('C', 'G')
        taxonomy.addChild('C', 'H')
        taxonomy.addChild('D', 'I')
        taxonomy.addChild('D', 'J')
        taxonomy.addChild('E', 'K')
        taxonomy.addChild('E', 'L')
        taxonomy.addChild('F', 'M')
        taxonomy.addChild('F', 'N')
                
        return taxonomy 
            
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
        
