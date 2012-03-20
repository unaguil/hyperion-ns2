import xml.dom.minidom as minidom
import re
import numpy
import gzip
import os
import sys
import time as timeUtil

import periodicValues.Util as Util

import datetime

import generic.Units as Units

import util.TimeFormatter as TimeFormatter

DEFAULT_PERIOD = 1.0

def get_class(clazz):
	parts = clazz.split('.')
	module = '.'.join(parts[:-1])
	m = __import__(module)
	for comp in parts[1:]:
		m = getattr(m, comp)
	return m

def createMeasure(clazz, period, simulationTime):
	className = clazz.split('.')[-1]
	measureClass = get_class(clazz + '.' + className)
	
	return measureClass(period, simulationTime)
	return None
		
class PeriodicEntry:
	def __init__(self, meanValues, stdValues, period, meanTotal, stdTotal, size):
		self.meanValues = meanValues
		self.stdValues = stdValues
		self.period = period
		self.meanTotal = meanTotal
		self.stdTotal = stdTotal
		self.size = size

class Measures:
	def __init__(self, str, mainConfigBuffer):
		config = minidom.parseString(str)
		
		self.__entries = config.getElementsByTagName('entry')
		
		mainConfig = minidom.parseString(mainConfigBuffer.getvalue())
		
		measureNodes = mainConfig.getElementsByTagName('measure')
		
		for entry in self.__entries:
			value = entry.firstChild.data
			key = entry.getAttribute("key")
			
			if key == 'finishTime':
				self.__simulationTime = float(value)
			if key == 'discardTime':
				self.__discardTime = float(value)

		self.__measureData = {}
		
		for measureNode in measureNodes:
			clazz = 'measures.' + measureNode.getAttribute('type')
			periodStr = measureNode.getAttribute('period');
							
			if periodStr is not '':
				period = float(periodStr)
			else:
				period = DEFAULT_PERIOD
			
			units, discardable = self.__getMeasureInfo(clazz, period)
			
			self.__measureData[clazz] = (clazz, period, units, discardable)
		
		self.__simulationFinished = False
		
		self.finishedSimulations = [] 
	
	def __getMeasureInfo(self, clazz, period):
		measure = createMeasure(clazz, period, self.__simulationTime)
		return measure.getUnits(), measure.isDiscardable()

	def startConfiguration(self, n, tag, type, simulationTime, discardTime):
		self.__currentConfiguration = (n, tag, type, simulationTime, discardTime)
		self.__currentResults = {}
		for measure in self.__measureData.keys():
			self.__currentResults[measure] = []
			
		self.__repeatStatus = [] 
		
	def getData(self, tempDir, outputLog): 				
		return (self.__measureData.values(), tempDir, outputLog, self.__simulationTime, self.__discardTime)
					
	def repeatsProcessed(self, results):
		for repeatFinished, measureResults in results:
			for measureType, measures in measureResults:
				self.__currentResults[measureType] .append(measures)
				
			self.__repeatStatus.append(repeatFinished)
		
	def __repeatsFinished(self):
		return all(self.__repeatStatus)

	def endConfiguration(self):
		configurationResults = {}
				
		for measure in self.__currentResults.keys():
			values = self.__currentResults[measure]
			(meanValues, stdValues, meanTotal, stdTotal) = self.__calculateStatistics(values)
			configurationResults[measure] = PeriodicEntry(meanValues, stdValues, self.__measureData[measure][1], meanTotal, stdTotal, len(values))
			
		n, tag, type, simulationTime, discardTime = self.__currentConfiguration
		
		if not self.__repeatsFinished():	
			return self.__getXMLError(n, tag, type)
		else:
			return self.__getXMLConfigurationResults(configurationResults, n, tag, type)	
			
	def savePartialResults(self, filePath):		
		resultsFile = open(filePath, 'w')
		for measure in self.__currentResults.keys():
			values = self.__currentResults[measure]
			resultsFile.write('Measure: %s\n' % measure)
			for index, (periodicValues, total) in enumerate(values):
				 resultsFile.write('\tRepeat: %d\n' % index)
				 resultsFile.write('\t\tTotal: %s\n' % str(total))
				 resultsFile.write('\t\tPeriodicValues: %s\n' % str(periodicValues.getValues()))
				 resultsFile.write('\n')
		resultsFile.close()		
				
	def __calculateStatistics(self, valuesArray):
		meanValues = []
		stdValues = []
		
		#get max size
		sizes = (len(periodicValues) for periodicValues, totalValues in valuesArray)
		size = max(sizes)
		
		totals = [totalValues for periodicValues, totalValues in valuesArray]
		 
		for i in xrange(size):
			values = []			
			for periodicValues, totalValues in valuesArray:
				values.append(periodicValues.getValue(i))
					
			meanValues.append(numpy.mean(values))	
			stdValues.append(numpy.std(values))
				
		return (meanValues, stdValues, numpy.mean(totals), numpy.std(totals))
	
	def __getXMLError(self, n, tag, type):
		doc = minidom.Document()
		
		configurationNode = doc.createElement('configuration')
		doc.appendChild(configurationNode)
		
		configurationNode.setAttribute('number', str(n))
		configurationNode.setAttribute('tag', tag)
		configurationNode.setAttribute('type', type)
		configurationNode.setAttribute('simulationFinished', 'no')
		
		return doc.toprettyxml()
												
	def __getXMLConfigurationResults(self, configurationResults, n, tag, type):
		doc = minidom.Document()
		
		configurationNode = doc.createElement('configuration')
		doc.appendChild(configurationNode)
	
		configurationNode.setAttribute('tag', tag)
		configurationNode.setAttribute('type', type)
	
		#Store date
		configurationNode.setAttribute('creationDate', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
		
		configurationNode.setAttribute('number', str(n))
		
		for entry in self.__entries:
			configurationNode.appendChild(entry)
						
		for measureName in sorted(self.__measureData.keys()):
			measureNode = doc.createElement('measure')
			configurationNode.appendChild(measureNode)
			measureNode.setAttribute('type', measureName[measureName.index('.') + 1:])
			
			clazz, period, units, discardable = self.__measureData[measureName]
			
			measureNode.setAttribute('period', str(period))
			measureNode.setAttribute('units', units)
			resultNode = doc.createElement('result')
			
			entry = configurationResults[measureName]
			resultNode.setAttribute('meanTotal', Units.str_formatter(units, entry.meanTotal))
			resultNode.setAttribute('stdTotal', Units.str_formatter(units, entry.stdTotal))
			resultNode.setAttribute('sampleSize', '%d' % entry.size)
			
			discardIndex = Util.getPeriod(self.__discardTime, entry.period, self.__simulationTime)
			for index, mean in enumerate(entry.meanValues):
				if index >= discardIndex or not discardable:
					valueNode = doc.createElement('entry')
					valueNode.setAttribute('mean', Units.str_formatter(units, mean))
					valueNode.setAttribute('std', Units.str_formatter(units, entry.stdValues[index]))
					time = index * entry.period
					valueNode.setAttribute('time', str(time))
					resultNode.appendChild(valueNode) 
			measureNode.appendChild(resultNode)
					
		return doc.toprettyxml()
	
compiledFinishedPattern = re.compile(r'INFO  peer.BasicPeer  - Simulation finished.*?')
compiledTimePattern = re.compile(r'.*?([0-9]+\,[0-9]+)$')

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
	        
def getLogLineTime(line):
    m = compiledTimePattern.match(line)
    if m is not None: 
        return float(m.group(1).replace(',', '.'))
    else:
        return 0.0
    
def checkFinished(line):
    m = compiledFinishedPattern.match(line)
    if m is not None:
        return True
    return False

def process(data):
    measures, tempDir, outputLog, simulationTime, discardTime = data
    currentMeasures = []
    for clazz, period, units, discardable in measures:
        measure = createMeasure(clazz, period, simulationTime)
        currentMeasures.append(measure)
        measure.start(tempDir)
        
    repeatFinished = False
    
    print '* Output log %s file size %s' % (outputLog, sizeof_fmt(os.path.getsize(outputLog)))
    sys.stdout.flush()
    
    logProcessStartTime = timeUtil.time()
    
    outputFile = gzip.open(outputLog, 'r')
    
    line = outputFile.readline()
    while (line != '' ):
        line.replace( '\n', '' )
    
        repeatFinished = checkFinished(line)

        time = getLogLineTime(line)                    
        #Parse line using each measure
        for measure in currentMeasures:
            if time >= discardTime or not measure.isDiscardable():
                measure.parseLine(line)

        line = outputFile.readline()
        
    outputFile.close()
    
    print '* Output log %s parsing time: %s' % (outputLog, TimeFormatter.formatTime(timeUtil.time() - logProcessStartTime))
    print ''
    sys.stdout.flush()
    
    results = []
    for measure in currentMeasures:
        measure.finish()
        results.append((measure.getType(), (measure.getValues(), measure.getTotalValue())))
        
    return repeatFinished, results	
