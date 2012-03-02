import random
import os
import math
from time import time

import util.TimeFormatter as TimeFormatter
import util.SimTimeRange as SimTimeRange

from xml.dom import minidom

from Service import Service
from Taxonomy import Taxonomy

class CompositionsPopulator:
    """Provides functions to create compositions and services for different nodes using a set of restrictions
       It also includes a function to generate the XML configuration for each node in the format used in simulations.
    """
    def __init__(self, entries):
        self.__nCompositions = None
        
        self.__sDistribution = 1.0
        
        self.__dDistribution = ()
        self.__wDistribution = ()
        self.__oDistribution = ()
        self.__compositionLength = 1
        self.__compositionWidth = 1
        self.__oNumber = 1
        
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "finishTime":
                self.__finishTime = float(value)   
            if key == "discardTime":
                self.__discardTime = float(value)
            if key == 'timeRange':
                self.__timeRange = eval(value)
            if key == "searchFreq":
                self.__searchFreq = float(value)
            if key == "oDistribution":
                self.__oDistribution = eval(value)
            if key == "oNumber":
                self.__oNumber = int(value)
            if key == "nDistribution":
                self.__nDistribution = float(value)    
            #all compositions are valid
            if key == "lDistribution":
                self.__dDistribution = eval(value)
            if key == "compositionLength":
                self.__compositionLength = int(value)
            if key == "compositionWidth":
                self.__compositionWidth = int(value)
            if key == "wDistribution":
                self.__wDistribution = eval(value)
            if key == 'nNodes':
                self.__nNodes = int(value)
                
            if key == 'nCompositions':
                self.__nCompositions = int(value)
                
        self.__serviceNameGenerator = self.__nameGenerator()
        self.__parameterNameGenerator = self.__nameGenerator()
        
        init, end = SimTimeRange.getTimeRange(self.__timeRange, self.__finishTime, self.__discardTime)
    
        if self.__nCompositions is None:
            self.__nCompositions = int(math.ceil((end - init) * self.__searchFreq))
    
    def generate(self, workingDir, strBuffer):
        self.__workingDir = workingDir
        self.__servicesDir = os.path.join(self.__workingDir, 'services')
        self.__solutionsDir = os.path.join(self.__servicesDir, 'solutions')
                    
        strBuffer.writeln('')
        strBuffer.writeln('************* Composition populator ****************')
        
        startTime = time()
        self.__generate(strBuffer)
        strBuffer.writeln('* Compositions generation time: %s ' % TimeFormatter.formatTime(time() - startTime))

        strBuffer.writeln('****************************************************')
    
    def __generate(self, strBuffer):                
        compositionsWithSolutions = int(self.__nCompositions * self.__sDistribution)
        compositionsWithoutSolutions = self.__nCompositions - compositionsWithSolutions
         
        strBuffer.writeln('* Nodes: %d' % self.__nNodes)   
        strBuffer.writeln('* Total compositions: %d' % self.__nCompositions)
        #strBuffer.writeln('* Solution distribution: %s -> (%d, %d)' % (self.__sDistribution, compositionsWithSolutions, compositionsWithoutSolutions))
        
        if self.__oDistribution:
            strBuffer.writeln('* CompositionIO: %s' % str(self.__oDistribution))
        else:
            strBuffer.writeln('* Outputs per service: %d' % self.__oNumber)
        
        if self.__dDistribution:
            strBuffer.writeln('* Length distribution: %s' % str(self.__dDistribution))
        else:
            strBuffer.writeln('* Composition length: %d' % self.__compositionLength)
            
        if self.__wDistribution:
            strBuffer.writeln('* Width distribution: %s' % str(self.__wDistribution))
        else:
            strBuffer.writeln('* Composition width: %d' % self.__compositionWidth)
        
        self.__createServiceDirectory(strBuffer)
     
        if self.__dDistribution:
            dDistributionTable = self.__getDistributionTable(compositionsWithSolutions, self.__dDistribution, 'dDistribution')
        else:
            dDistributionTable = [(self.__nCompositions, self.__compositionLength)]
            
        if not self.__wDistribution:
            self.__wDistribution = (self.__compositionWidth, self.__compositionWidth)
            
        if not self.__oDistribution:
            self.__oDistribution = (self.__oNumber, self.__oNumber)
        
        self.__compositions = []
        services = []
        
        self.__checkRange(self.__oDistribution, 'ioDistribution')
        self.__checkRange(self.__wDistribution, 'wDistribution')
        
        for numCompositions, maxDepth in dDistributionTable:
            for i in xrange(numCompositions):
                composition, compositionGraph = self.__createComposition(maxDepth, False)
                self.__compositions.append(composition)
                
                self.__generateXMLCompositionGraph(composition, compositionGraph)
                
                for compositionServices in compositionGraph.values():
                    services += compositionServices
        
        for i in xrange(compositionsWithoutSolutions):
            composition, compositionServices = self.__createComposition(5, True)
            self.__compositions.append(composition)
            services += compositionServices

        strBuffer.writeln('* Generated services: %d' % len(services))
        strBuffer.writeln('* Generated parameters: %d' % self.getParameters(services))
        
        subsetSize = 0
        nodes = {}  
        if self.__nDistribution > 0.0:
            subsetSize = int(round(self.__nNodes * self.__nDistribution))
            if subsetSize < 1:
                subsetSize = 1
                
            shuffledNodes = range(self.__nNodes)
            random.shuffle(shuffledNodes)
            shuffledNodes = shuffledNodes[:subsetSize]
        
            #distribute services among nodes
            for service in services:
                index = random.randrange(subsetSize)
                node = shuffledNodes[index]
                if not node in nodes:
                    nodes[node] = []
                nodes[node].append(service)
                
            subsetSize = len(shuffledNodes) 
                
        strBuffer.writeln('* Service distribution: %s' % self.__nDistribution)
        strBuffer.writeln('* Nodes with services: %d' % subsetSize)
        
        taxonomy = Taxonomy('TaxonomyRootElement')
        self.__generateXMLNodeConfigurations(self.__compositions, nodes, taxonomy)
        
    def getCompositions(self):
        return self.__compositions
    
    def getParameters(self, services):
        totalParameters = 0
        for service in services:
            totalParameters += len(service.getInputs()) + len(service.getOutputs())
        return totalParameters
        
    def __createComposition(self, maxDepth, invalid):
        serviceName = "Composition-" + self.__serviceNameGenerator.next()
        composition = Service(serviceName)
        
        for i in xrange(self.__getRandomParameterNumber()):
            composition.addInput(self.__parameterNameGenerator.next())
            
        currentOutputs = self.__getInitOutputs(composition)
        
        services = {}
        compositionOutputs = self.__createGraph(currentOutputs, services, 0, maxDepth, invalid)
        for output in self.__getOutputList(compositionOutputs):
            composition.addOutput(self.__getParamID(output))
    
        return composition, services
    
    def __getOutputList(self, outputs):
        outputList = []
        for parameters in outputs:
            outputList += parameters
        return outputList
    
    def __getRandomParameterNumber(self):
        return random.randrange(self.__oDistribution[0], self.__oDistribution[1] + 1)
    
    def __selectOutputs(self, outputs):
        selectedOutputs = []
        for parameters in outputs:
            selectedOutputs += parameters
        return selectedOutputs
    
    def __createGraph(self, currentOutputs, services, currentDepth, maxDepth, invalid):
        #create next services
        nextServices = []
        for i in xrange(random.randrange(self.__wDistribution[0], self.__wDistribution[1] +  1)):
            nextService = Service('Service-' + self.__serviceNameGenerator.next())
            selectedInputs = self.__convertToInputs(self.__selectOutputs(currentOutputs))
            for input in selectedInputs:
                nextService.addInput(self.__getParamID(input))
                
            for i in xrange(self.__getRandomParameterNumber()):
                nextService.addOutput(self.__parameterNameGenerator.next())
            
            nextServices.append(nextService)
            
        currentDepth += 1
            
        if invalid and self.__stopGeneration(currentDepth, maxDepth):
            randomOutputs = []
            for i in xrange(self.__getRandomParameterNumber()):
                randomOutputs.append(self.__parameterNameGenerator.next())
            return randomOutputs
            
        services[currentDepth] = []
        services[currentDepth] += nextServices
        currentOutputs = self.__getOutputs(nextServices)
        if currentDepth < maxDepth:
            return self.__createGraph(currentOutputs, services, currentDepth, maxDepth, invalid)
        else:
            return currentOutputs    
        
    def __stopGeneration(self, currentDepth, maxDepth):
        #stop probability increases with depth        
        if currentDepth >= maxDepth:
            return True
        
        value = random.randrange(maxDepth - currentDepth)
        return value == 0
    
    def __getOutputs(self, services):
        outputs = []
        for service in services:
            outputs.append(service.getOutputs())
        return outputs
    
    def __getInitOutputs(self, composition):
        return [self.__convertToOutputs(composition.getInputs())]
    
    def __getGoalInputs(self, composition):
        return self.__convertToInputs(composition.getOutputs())
    
    def __getParamID(self, p):
        return p[p.find('-') + 1:]
    
    def __convertToOutputs(self, parameters):
        outputs = []
        for p in parameters:
            output = 'O-' + p[p.find('-') + 1:]
            outputs.append(output)
        return outputs
    
    def __convertToInputs(self, parameters):
        outputs = []
        for p in parameters:
            output = 'I-' + p[p.find('-') + 1:]
            outputs.append(output)
        return outputs
        
    def __nameGenerator(self):
        currentName = 0
        while True:
            yield '%d' % currentName
            currentName += 1
    
    def __checkRange(self, range, str):
        if range[0] < 1 or range[1] < 1:
            raise Exception('Range ' + str + ' should be positive and greater or equal than 1')
        
    def __getTotalSolutions(self, sDistributionTable):
        totalSolutions = 0;
        for compositions, solutions in sDistributionTable:
            totalSolutions += compositions * solutions
        return totalSolutions
    
    def __checkDistribution(self, distribution, str):
        total = round(sum([percentage for percentage, value in distribution]), 2)
        
        if not total == 1.0:
            raise Exception('Distribution ' + str + ' percentages do not add to 1.0. Obtained %f instead' % total)
        
    def __getDistributionTable(self, elements, distribution, str):
        self.__checkDistribution(distribution, str)
           
        totalElements = 0
        
        distributionTable = []
        
        for index, (percentage, values) in enumerate(distribution):
            calculatedElements = int(round(elements * percentage))
            if index == len(distribution) - 1:
                calculatedElements = elements - totalElements
            distributionTable.append((calculatedElements, values))
            totalElements += calculatedElements
            
        return distributionTable
    
    def __createServiceDirectory(self, strBuffer):
        strBuffer.writeln('* Creating %s directory ' % self.__servicesDir)
        os.mkdir(self.__servicesDir)
        os.mkdir(self.__solutionsDir)
    
    def __generateXMLCompositionGraph(self, composition, compositionGraph):                                        
        doc = minidom.Document()
        compositionGraphElement = doc.createElement('compositionGraph')
        doc.appendChild(compositionGraphElement);
        for layer in sorted(compositionGraph.keys()):
            layerElement = doc.createElement("layer")
            layerElement.setAttribute('depth', str(layer))
            compositionGraphElement.appendChild(layerElement)
            for service in compositionGraph[layer]:
                serviceElement = doc.createElement('service')
                serviceElement.setAttribute('name', service.getID())
                layerElement.appendChild(serviceElement)
            
        filePath =  os.path.join(self.__solutionsDir, composition.getID() + '.xml') 
        oFile = open(filePath, 'w')
        oFile.write(doc.toprettyxml())
        oFile.close();
    
    def __generateXMLNodeConfigurations(self, compositions, nodes, taxonomy):                
        taxonomyFilePath = os.path.join(self.__workingDir, 'taxonomy.xml')
        oFile = open(taxonomyFilePath, 'w')
        xmlTaxonomy = taxonomy.createXMLDocument() 
        oFile.write(xmlTaxonomy.toprettyxml())
        oFile.close()
        
        self.__writeCompositions(compositions)
        
        self.__writeNodeServices(nodes)
        
    def __writeNodeServices(self, nodes):
        for node in nodes.keys():
            servicesFilePath = os.path.join(self.__servicesDir, 'Services' + str(node) + '.xml')
            oFile = open(servicesFilePath, 'w')
            doc = self.__createServicesXMLDocument(nodes[node])
            oFile.write(doc.toprettyxml())
            oFile.close()
    
    def __createServicesXMLDocument(self, services):
        doc = minidom.Document()
        
        servicesElement = doc.createElement('services')
        doc.appendChild(servicesElement)
        for service in services:
            service.addXMLService(servicesElement, doc)
            
        return doc
        
    def __writeCompositions(self, compositions):
        compositionsFilePath = os.path.join(self.__servicesDir, 'Services.xml')
        oFile = open(compositionsFilePath, 'w')
        doc = self.__createServicesXMLDocument(compositions)
        oFile.write(doc.toprettyxml())
        oFile.close()
