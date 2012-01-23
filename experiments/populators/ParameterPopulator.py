import os

from xml.dom import minidom

from Taxonomy import Taxonomy

import random

class IncorrectSolution(Exception):
    def __init__(self):
        pass

class ParameterPopulator:
    """Provides functions to populate a the list of parameters for a set of nodes
       It also includes a function to generate the XML configuration for each node in the format used in simulations.
    """
    def __init__(self, entries):
        self.__equalityDistribution = {}
        
        self.__usedConcepts = []
        
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "nNodes":
                self.__nNodes = int(value)
            if key == "nDistribution":
                self.__nDistribution = float(eval(value))
            if key == "parametersPerNode":
                self.__parametersPerNode = int(eval(value))
            if key == 'equalityDistribution':
                self.__equalityDistribution = eval(value)
    
    def generate(self, workingDir, strBuffer):            
        strBuffer.writeln('')
        strBuffer.writeln('************* Parameter populator ****************')
        parametersTable, taxonomy = self.__generate(self.__nNodes, self.__nDistribution, self.__parametersPerNode, self.__equalityDistribution, strBuffer)    
        
        self.__generateXMLNodeConfigurations(workingDir, parametersTable, taxonomy, strBuffer)

        strBuffer.writeln('**************************************************')
        
    def getUsedConcepts(self):
        return set(self.__usedConcepts)
    
    def __generate(self, nNodes, nDistribution, parametersPerNode, equalityDistribution, strBuffer):
        nodesWithParameters = int(nNodes * nDistribution)
                    
        strBuffer.writeln('* Node distribution: %.2f' % nDistribution)
        strBuffer.writeln('* Nodes with parameters: %d' % nodesWithParameters)
        strBuffer.writeln('* Parameters per node: %d' % parametersPerNode)
        
        if len(equalityDistribution) > 0:
            strBuffer.writeln('* Using an equality distribution of %s' % str(equalityDistribution))
        
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
            nodeTable[node] = []
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
            self.__usedConcepts += taxonomy.getParents(type)
            
        generatedParameters = self.__countParameters(nodeTable) 
            
        remainingParameters = nodesWithParameters * parametersPerNode - generatedParameters
        for i in xrange(remainingParameters):
            p = generator.next()
            parameters.append(p)
            taxonomy.addChild('Root', p)
            self.__usedConcepts.append(p)
            
        random.shuffle(parameters)
        
        for node in nodeTable.keys():
            selectedParameters = parameters[:parametersPerNode]
            del parameters[:parametersPerNode]
            nodeTable[node] += selectedParameters
                                
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
        
    def __generateXMLNodeConfigurations(self, workingDir, parametersTable, taxonomy, strBuffer):        
        dir = os.path.join(workingDir, 'parameters')
        
        strBuffer.writeln('* Creating %s directory ' % dir)
        os.mkdir(dir)
        
        taxonomyFilePath = os.path.join(workingDir, 'taxonomy.xml')
        oFile = open(taxonomyFilePath, 'w')
        xmlTaxonomy = taxonomy.createXMLDocument() 
        oFile.write(xmlTaxonomy.toprettyxml())
        oFile.close()
        
        for node in parametersTable.keys():
            if len(parametersTable[node]) > 0:
                filePath = os.path.join(dir, 'Parameters' + str(node) + '.xml')
                self.__generateXML(node, set(parametersTable[node]), filePath)
        