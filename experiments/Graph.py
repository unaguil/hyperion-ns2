#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy
import os
import sys

from optparse import OptionParser

import xml.dom.minidom as minidom

from matplotlib.backends.backend_pdf import PdfPages

from measures.generic.GenericAvgMeasure import GenericAvgMeasure

def __relStd(mean, std):
	return 100 * std / mean

def get_class(clazz):
	parts = clazz.split('.')
	module = '.'.join(parts[:-1])
	m = __import__(module)
	for comp in parts[1:]:
		m = getattr(m, comp)
	return m

def createMeasure(clazz, period):
	className = clazz.split('.')[-1]
	measureClass = get_class(clazz + '.' + className)
	
	return measureClass(period, 10.0)

class PeriodicResult:
	def __init__(self, tag, period, values, meanTotal, stdTotal, sampleSize):
		self.__tag = float(tag)
		self.__period = period
		self.__values = values
		self.__meanTotal = meanTotal
		self.__stdTotal = stdTotal
		self.__sampleSize = sampleSize
	
	def getTag(self):
		return self.__tag		
	
	def getPeriod(self):
		return self.__period
		
	def getRelStdValues(self):
		relStdValues = []
		for mean, std, time in self.__values:
			if mean == 0:
				relStdValues.append(0)
			else: 
				relStdValues.append(100 * std / mean)
		return relStdValues
	
	def getValues(self):
		means, stds, times = zip(*self.__values)
		return means, stds, times
	
	def getMeanTotal(self):
		return self.__meanTotal

	def getStdTotal(self):
		return self.__stdTotal
	
	def getSampleSize(self):
		return self.__sampleSize
	
	def geStdTotal(self):
		return self.__stdTotal

class Graph:
	def __init__(self, files, lang, errorBar):
		self.__errorBar = errorBar
		self.__measureNames = self.__loadMeasureNames(lang)
		
		self.__measures = self.__loadFiles(files)
		
	def __loadFiles(self, files):
		loadedMeasures = {}
		
		for file in files:
			print 'Parsing file %s' % file
			
			try:
				parser = minidom.parse(file)
				
				measures = parser.documentElement
				tag = measures.getAttribute('tag')
				type = measures.getAttribute('type')
				
				simulationFinished = measures.getAttribute('simulationFinished')
				
				if simulationFinished == 'no':
					print 'ERROR: There are error in %s output file' % file
					sys.exit()			
				
				measureNodes = parser.getElementsByTagName('measure')
				for measureNode in measureNodes:
					mType = measureNode.getAttribute('type')
					period = measureNode.getAttribute('period')
					units = measureNode.getAttribute('units')
					resultNodes = measureNode.getElementsByTagName('result') 

					print 'Parsing measure %s' % mType
					
					if not mType in loadedMeasures:
						loadedMeasures[mType] = (type, units, [])
					
					for resultNode in resultNodes:
						sampleSize = int(resultNode.getAttribute('sampleSize'))
						meanTotal = float(resultNode.getAttribute('meanTotal'))
						stdTotal = float(resultNode.getAttribute('stdTotal'))
						
						entryNodes = resultNode.getElementsByTagName('entry')

						values = []
						for entryNode in entryNodes:
							mean = float(entryNode.getAttribute('mean'))
							std = float(entryNode.getAttribute('std'))
							time = float(entryNode.getAttribute('time'))
							values.append((mean, std, time))

						result = PeriodicResult(tag, float(period), values, meanTotal, stdTotal, sampleSize)
						
						expectedType = loadedMeasures[mType][0]
						if not type == expectedType:
							print 'ERROR: Trying to merge incompatible types'
							sys.exit()
						
						loadedMeasures[mType][2].append(result)
			except Exception as e:
				print 'ERROR: Parser error processing file %s. Cause: %s' % (file, e.message)
				sys.exit()
				
			return loadedMeasures
	
	def getMeasures(self):
		return self.__measures.keys()
	
	def __loadMeasureNames(self, lang):
		measureNames = {}
		
		try:
			file = open('measureNames.' + lang)
			for line in file:
				entry = line.split('=')
				if len(entry) == 2:
					key = entry[0].strip()
					value = entry[1].strip()
					if not value == '':
						measureNames[key] = value
				
		except IOError:
			print 'Error: Could not load measure names file.'
			sys.exit()
			
		return measureNames
	
	def __checkUnits(self, measures, measureTypes):
		values = []
		
		for measureType in measureTypes:
			name, units, results = measures[measureType]
			values.append(units)
			
		values = set(values)
		
		if len(values) > 1:
			print 'ERROR: Trying to plot measures with different units'
			sys.exit()
			
	def __checkMeasureTypes(self, measures, measureTypes):
		for measureType in measureTypes:
			if not measureType in measures:
				print 'Unknown measure %s' % measureType
				sys.exit()
	
	def plotTotal(self, measureTypes, xLabel=None, yLabel=None, xAxis=None, yAxis=None):
		self.__checkMeasureTypes(self.__measures, measureTypes)			
		self.__checkUnits(self.__measures, measureTypes)
		
		lines = []
		labels = []						

		for measureType in measureTypes:			
			x = []
			y = []
		
			stdValues = []
			relStdValues = []
		
			name, units, results = self.__measures[measureType] 
			for result in results:
				x.append(result.getTag())
				y.append(result.getMeanTotal())
				stdValues.append(result.getStdTotal())
				
				if result.getMeanTotal() == 0:
					relStdValues.append(0)
				else:
					relStdValues.append(100 * result.getStdTotal() / result.getMeanTotal())
			
			data = dict(zip(x,zip(y, stdValues)))
			x = sorted(x)
			y = [data[i][0] for i in x]
			yerrors = [data[i][1] for i in x]

			print 'Plotting %s measure type' % measureType
			print "X: ", x
			print "Y: ", y
			print "YErrors: ", yerrors
			
			if not xLabel is None:
				plt.xlabel(xLabel)
			else:
				plt.xlabel(name)
				
			label, measure, units = self.__getMeasureInfo(measureType)
		
			self.__printTotalInfo(y, stdValues, relStdValues, label, '')
	
			if self.__errorBar:	
				line = plt.errorbar(x, y, yerrors, label=label, fmt='kx--')
			else:
				line = plt.plot(x, y, 'kx--')
	
			lines.append(line)
			labels.append(label)
		
		if not yLabel is None:
			plt.ylabel(yLabel)
		else:
			yLabel = "%s [%s]" % (label, units)
			plt.ylabel(yLabel)

		plt.xticks(x)

		self.__setAxis(plt, xAxis, yAxis) 

		#plt.figlegend(lines, labels, 'upper right')
		
	def finishPlotting(self, plt, fName, format='DISPLAY'):
		if format == 'DISPLAY':
			plt.show()
		else:
			plt.savefig(fName, format=format)
	
	def __getMeasureInfo(self, measureType):
		measureClass = 'measures.' + measureType
		measure = createMeasure(measureClass, 5.0)
		if measureClass in self.__measureNames:
			return self.__measureNames[measureClass], measure, measure.getUnits() 
		else:
			return measure.getName(), measure, measure.getUnits()
			
	def __setAxis(self, plt, xAxis, yAxis, defaultXAxis = None):
		axis = list(plt.axis())

		if defaultXAxis is not None:
			axis[0] = defaultXAxis[0]
			axis[1] = defaultXAxis[1]
			
		axis[2] = 0
		#axis[3] = axis[3] * 1.10

		if xAxis is not None:
			axis[0] = float(xAxis[0])
			axis[1] = float(xAxis[1])
			
		if yAxis is not None:
			axis[2] = float(yAxis[0])
			axis[3] = float(yAxis[1])

		#plt.grid(True)
			
		plt.axis(axis)
		
	def plotPeriodic(self, measureTypes, yLabel=None, xAxis=None, yAxis=None):
		self.__checkMeasureTypes(self.__measures, measureTypes)			
		self.__checkUnits(self.__measures, measureTypes)

		plt.xlabel('time [s]')
		
		lines = []
		labels = []
			
		plt.grid(True)
		for measureType in measureTypes:			
			if not measureType in self.__measures:
				print 'ERROR: Unknown measure %s' % measureType
				sys.exit()
			else:			
				name, units, results = self.__measures[measureType]
				for result in results: 
					means, stds, times = result.getValues()
					relStdValues = result.getRelStdValues() 
					
					#print "X: ", x
					#print "Y: ", y
			
					measureName, measure, units = self.__getMeasureInfo(measureType)
			
					label = '%s (%s %s)' % (measureName, result.getTag(), name)
					
					self.__printPeriodicInfo(means, times, stds, relStdValues, label, '')
			
					line = plt.plot(times, means)
					
					if isinstance(measure, GenericAvgMeasure):
						#draw average line
						avgValues = [result.getMeanTotal()] * len(times)
						avgLine = plt.plot(times, avgValues)
						avgLabel = 'Avg. of %s: %s %s' % (measureName, result.getMeanTotal(), units)
						lines.append(avgLine)
						labels.append(avgLabel)
					else:
						label += '\nTotal: %s %s' % (result.getMeanTotal(), units)
						
					lines.append(line)
					labels.append(label)
		
		if not yLabel is None:
			plt.ylabel(yLabel)
		else:
			plt.ylabel(units) 
			
		self.__setAxis(plt, xAxis, yAxis, (min(times), max(times)))
		
		plt.figlegend(lines, labels, 'upper right')  
		
	def printSummary(self):
		for measureType in sorted(self.__measures):
			name, units, results = self.__measures[measureType]
			print 'Measure: %s [%s]' % (measureType, units)
			tagValues = {}
			for result in results:
				tagValues[result.getTag()] = result	
			
			for tag in sorted(tagValues.keys()):
				result = tagValues[tag]
				print ' *%s: %s mean: %.2f std: %.2f' % (name, tag, result.getMeanTotal(), result.getStdTotal())
				
	def plotAll(self, format, onePDF, outputFile, periodic=False):
		if onePDF:
			rowsPerPage = 1
			columnsPerPage = 1
			plotsPerPage = rowsPerPage * columnsPerPage
			pp = PdfPages(outputFile)
			
			for index, measure in enumerate(sorted(self.__measures)):
				
				plotNumber = index % plotsPerPage
				if plotNumber == 0:
					plt.clf() 
					plt.figure(index / plotsPerPage + 1)
					 
				plt.subplot(rowsPerPage, columnsPerPage, plotNumber + 1)
				if not periodic:
					self.plotTotal([measure])
				else:
					self.plotPeriodic([measure])
				
				if plotNumber + 1 == plotsPerPage:
					plt.savefig(pp, format='pdf')
				
			pp.close()
		else: 
			for measure in sorted(self.__measures):
				fName = measure + '.' + format
				plt.clf()
				if not periodic:
					self.plotTotal([measure])
				else:
					self.plotPeriodic([measure])
				self.finishPlotting(plt, fName, format) 
				
	def __printPeriodicInfo(self, data, times, stdValues, relStdValues, label, units):
		print ''
		print 'Plotting periodic data label=\'%s\':' % label
		print '\t*Size: %d elements' % len(data)
		print '\t*Time range: [%s,%s] s' % (min(times), max(times))
		print '\t*Max std: %.2f %s' % (max(stdValues), units)
		print '\t*Max relative std: %.2f%%' % max(relStdValues)
		print '\t*Mean relative std: %.2f%%' % numpy.mean(relStdValues)
		print '\t*Std of relative std: %.2f%%' % numpy.std(relStdValues)
		print ''
		
	def __printTotalInfo(self, data, stdValues, relStdValues, label, units):
		print ''
		print 'Plotting total data label=\'%s\':' % label
		print '\t*Size: %d elements' % len(data)
		print '\t*Max std: %.2f %s' % (max(stdValues), units)		
		print '\t*Max relative std: %.2f%%' % max(relStdValues)
		print '\t*Mean relative std: %.2f%%' % numpy.mean(relStdValues)
		print '\t*Std of relative std: %.2f%%' % numpy.std(relStdValues)
		print ''

def getXMLFiles(path):
	xmlFiles = []
	for file in os.listdir(path):
		filePath = os.path.join(path, file)
		if not os.path.isdir(filePath) and '.xml' in file:
			xmlFiles.append(filePath)
	
	return xmlFiles

def main():
	parser = OptionParser()
	parser.add_option("-i", "--input", dest="inputFile", help="experiment report used as input")
	parser.add_option("-d", "--directory", dest="directory", help="directory containing the result files to merge")
	parser.add_option("-p", "--periodic", dest="periodic", help="plots a periodic graph (default is total graph)", action="store_true", default=False)
	parser.add_option("-s", "--summary", dest="summary", help="prints the summary of the parsed files", action="store_true", default=False)
	parser.add_option("-a", "--all", dest="all", help="plots all measures each one in a separate image", action="store_true", default=False)
	parser.add_option("-f", "--format", dest="format", help='output format for plotted image', default='DISPLAY')
	parser.add_option("-o", "--onePDF", dest="onePDF", help='write plots to a multiple pages PDF', action="store_true", default=False)
	parser.add_option("-w", "--writeFile", dest="writeFile", help="plotting output file name", default=None)
	
	parser.add_option("--xLabel", dest="xLabel", help="sets the label for X axis")
	parser.add_option("--yLabel", dest="yLabel", help="sets the label for Y axis")
	parser.add_option("--xmin", dest="xmin", help="sets the min value for X axis")
	parser.add_option("--xmax", dest="xmax", help="sets the max value for X axis")
	parser.add_option("--ymin", dest="ymin", help="sets the min value for Y axis")
	parser.add_option("--ymax", dest="ymax", help="sets the max value for Y axis")
	parser.add_option("--errors", dest="errorBar", help="shows error bars", action="store_true", default=False)
	
	(options, args) = parser.parse_args()
	
	if options.inputFile is None and options.directory is None:
		parser.print_usage()
	else:
		files = []
		outputFile = 'allPlots.pdf'
		if not options.directory is None:
			files = getXMLFiles(options.directory)
			outputFile = os.path.join(options.directory, outputFile)
		else:
			files.append(options.inputFile)
			
		graph = Graph(files, 'en', options.errorBar)
		
		if options.all: 
			graph.plotAll(options.format, options.onePDF, outputFile, options.periodic)
			sys.exit()
			
		if options.summary:
			graph.printSummary()
			sys.exit()
		
		if len(args) == 0:
			if not options.summary:
				print 'Supported measures: %s' % graph.getMeasures()
			else:
				graph.printSummary()
		else:  					
			if not options.periodic:
				#Plot selected measure types				
				graph.plotTotal(args, options.xLabel, options.yLabel, (options.xmin, options.xmax), (options.ymin, options.ymax))
				graph.finishPlotting(plt, options.writeFile, options.format)
			else: 
				graph.plotPeriodic(args, options.yLabel, (options.xmin, options.xmax), (options.ymin, options.ymax))
				graph.finishPlotting(plt, options.writeFile, options.format)

if __name__ == '__main__':
	 main()

