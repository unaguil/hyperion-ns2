#!/usr/bin/python

import sys
import os
import shutil
import subprocess
import threading
import re
import time
import datetime
import multiprocessing
import StringIO

import util.StrBuffer as StrBuffer

from optparse import OptionParser

from ConfigGenerator import ConfigGenerator
from measures.Measures import Measures
from measures.Measures import process
from ScriptGenerator import ScriptGenerator

import util.TimeFormatter as TimeFormatter

import xml.dom.minidom as minidom

MAX_TRIES = 3

JVM_DUMP_CHECK_TIME = 1.0

class JVMCheckingTimer(threading.Thread):
	def __init__(self, period, process, tempDir):
		threading.Thread.__init__(self)
		
		self.setDaemon(True)
		
		self.__period = period
		self.__process = process
		self.__tempDir = tempDir
		
		self.__stop = False
		
	def run(self):
		while not self.__stop:
			try:
				for file in os.listdir(self.__tempDir):
					if re.match('hs_err_pid[0-9]+\.log', file) is not None:
						print '* ERROR: JVM failed during simulation. Killing process. See %s ' % os.path.join(self.__tempDir, file)
						self.__process.kill()
						return							
			except OSError:
				pass
			
			time.sleep(self.__period)
		
	def cancel(self):
		self.__stop = True

class RepeatRunner:
	def __init__(self, tempDir, config, workingDir, configGenerator, repeat, repeatNumber):
		self.__tempDir = tempDir
		self.__config = config
		self.__configDir = workingDir
		self.__configGenerator = configGenerator
		self.__repeat = repeat
		self.__repeatNumber = repeatNumber
		
		self.__try = 1 
		
	def __execute(self):
		strBuffer = StrBuffer.StrBuffer()
		strBuffer.writeln('* Running repeat %d of %d' % (self.__repeat + 1, self.__repeatNumber))
				
		#Create temporal directory and prepare configuration files
		if os.path.isdir(self.__tempDir):
			shutil.rmtree(self.__tempDir)
		
		os.mkdir(self.__tempDir)
		
		self.__prepareSimulationFiles(self.__tempDir, self.__config, self.__configDir)	
		
		#Create script using ScriptGenerator
		if self.__configGenerator.getDiscardTime() >= self.__configGenerator.getSimulationTime():
			strBuffer.writeln('* ERROR: Discard time %.2f should be smaller than simulation time %.2f ' % (self.__configGenerator.getDiscardTime(), self.__configGenerator.getSimulationTime()))
			print strBuffer.getvalue()
			sys.exit()
						
		scriptGenerator = ScriptGenerator(self.__config, strBuffer)
		scriptGenerator.generate('Script.tcl', self.__tempDir, self.__repeat, strBuffer)
		
		#Run script
		simStartTime = time.time()
		out = open(os.path.join(self.__tempDir, 'out'), 'w')
		err = open(os.path.join(self.__tempDir, 'err'), 'w')
		
		strBuffer.writeln('* Simulation script on directory %s try %d' % (self.__tempDir, self.__try))
		
		self.__p = subprocess.Popen(['ns', 'Script.tcl'], stdout=out, stderr=err, cwd=self.__tempDir)
		
		self.__timer = JVMCheckingTimer(JVM_DUMP_CHECK_TIME, self.__p, self.__tempDir) 
		self.__timer.start()
		
		print strBuffer.getvalue()
		sys.stdout.flush()
		
		success = self.__p.wait() == 0
		self.__timer.cancel()
		
		out.close()
		err.close() 
		
		strBuffer = StrBuffer.StrBuffer()
		
		if not success:
			strBuffer.writeln('* ERROR: There was a problem during simulation execution on directory %s' % self.__tempDir)
		else:
			strBuffer.writeln('* Finished NS-2 simulation on directory %s. Running time: %s' % (self.__tempDir, TimeFormatter.formatTime(time.time() - simStartTime)))
			self.__compressOutputLog(strBuffer)
			
		print strBuffer.getvalue()
		sys.stdout.flush()
			
		return success
	
	def terminate(self):
		self.__p.kill()
		self.__timer.cancel()
		
	def run(self):
		success = False
		while self.__try <= MAX_TRIES and not success:		
			success = self.__execute()
			self.__try += 1

		return success
			
	def __compressOutputLog(self, strBuffer):  
		startTime = time.time()
		strBuffer.writeln('* Compressing output log file %s' % self.__getPlainLog())
		p = subprocess.Popen(['gzip', self.__getPlainLog()])
		success = p.wait() == 0
		
		if not success:
			strBuffer.writeln('ERROR: There was a problem compressing file %s' % self.__getPlainLog())
		else:
			strBuffer.writeln('* Compressed log obtained in %s. Running time: %s' % (self.getOutputLog(), TimeFormatter.formatTime(time.time() - startTime))) 
		
		return success
	
	def __getPlainLog(self):
		return os.path.join(self.__tempDir, 'output.log')
	
	def getOutputLog(self):
		return os.path.join(self.__tempDir, 'output.log.gz')
	
	def getTempDir(self):
		return self.__tempDir
	
	def __prepareSimulationFiles(self, tempDir, config, workingDir):
		configFile = open(os.path.join(tempDir, 'Configuration.xml'), 'w')
		configFile.write(config)
		configFile.close()
		
		shutil.copy2('./common/WCommon.tcl', os.path.join(tempDir, 'WCommon.tcl'))
		
		shutil.copy2('log4j.properties', os.path.join(tempDir, 'log4j.properties'))
		
		#Copy all files contained in input directory to temporal directory
		for file in os.listdir(workingDir):
			srcPath = os.path.join(workingDir, file)
			dstPath = os.path.join(tempDir, file)
			if not os.path.isdir(srcPath):
				shutil.copy2(srcPath, dstPath)
				
def runRepeat(args):
	try:
		repeatDir, config, configDir, inputFile, configGenerator, counter, repeatNumber = args
				
		r = RepeatRunner(repeatDir, config, configDir, configGenerator, counter, repeatNumber)
		success = r.run()
		return (success, r.getOutputLog(), r.getTempDir())
	except KeyboardInterrupt:
		print '* Terminating process'
		r.terminate()

class Experiment:
	def __init__(self, configDir, inputFile, outputDir, debug, workingDir, processing, processes):
		self.__configDir = configDir
		self.__outputDir = outputDir
		self.__inputFile = os.path.join(self.__configDir, inputFile)
		self.__inputFileName = inputFile
		self.__debug = debug
		self.__workingDir = workingDir
		self.__processes = processes
		
		self.__compiledFinishedPattern = re.compile(r'INFO  peer.BasicPeer  - Simulation finished.*?')
		self.__compiledTimePattern = re.compile(r'.*?([0-9]+\,[0-9]+)$')
		
		if not processing and os.path.isdir(self.__workingDir):
			shutil.rmtree(self.__workingDir)
		
		if not processing:	
			os.mkdir(self.__workingDir)
		
			shutil.copy2(self.__inputFile, self.__workingDir)
			
	def __saveTimestamp(self, dir):
		oFile = open(os.path.join(dir, 'launched.txt'), 'w')
		oFile.write("Experiment started on: %s " % datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
		oFile.close()
		
	def __resolveImports(self, filePath):
		buffer = StringIO.StringIO()
		
		doc = minidom.parse(filePath)
		
		replacedImports = {}		
		for importTag in doc.getElementsByTagName('import'):
			importedFilePath = self.__configDir + '/' + importTag.getAttribute('file')
			importedDoc = minidom.parse(importedFilePath)
			partTag = importedDoc.getElementsByTagName('part')[0]
			replacedImports[importTag] = partTag.childNodes			
		
		for replacedImport in replacedImports.keys():
			parent = replacedImport.parentNode
			for child in replacedImports[replacedImport]:
				newNode = doc.importNode(child, True) 
				parent.insertBefore(newNode, replacedImport)
			parent.removeChild(replacedImport)
		
		buffer.writelines(doc.toxml())
		return buffer 		

	def __run(self):				
		resolvedFileBuffer = self.__resolveImports(self.__inputFile)
		configGenerator = ConfigGenerator(resolvedFileBuffer)
		configurationCounter = 0		
		self.__saveTimestamp(self.__workingDir)
		
		while configGenerator.hasNext():
			configurationDir = os.path.join(self.__workingDir, 'configuration-' + str(configurationCounter))
			
			os.mkdir(configurationDir)
			
			startTime = time.time()
			
			repeatNumber = configGenerator.getRepeat()
			
			print ''
			print "* Running experiment configuration %d with %d repetition(s)" % (configurationCounter + 1, repeatNumber)
			print ''
			sys.stdout.flush() 
			#Get current execution configuration
			config, generatedExpConfig = configGenerator.next()
			
			measures = Measures(config, resolvedFileBuffer)
			
			measures.startConfiguration(configurationCounter, configGenerator.getTag(), configGenerator.getType(), configGenerator.getSimulationTime(), configGenerator.getDiscardTime())
			
			#save current configuration
			generatedConfigFile = open(os.path.join(configurationDir, 'GeneratedConfig.xml') , 'w')
			generatedConfigFile.write(generatedExpConfig)
			generatedConfigFile.close()						
			
			data = []
			
			for counter in range(repeatNumber):		
				repeatDir = os.path.join(configurationDir, 'repeat-' + str(counter))
				data.append((repeatDir, config, self.__configDir, resolvedFileBuffer, configGenerator, counter, repeatNumber))
				
			pool = multiprocessing.Pool(processes=self.__processes)
			results = pool.map(runRepeat, data) 

			success = all([success for success, outputLog, tempDir in results])
			
			if not success:
				print '* Errors during execution of configuration %d' % configurationCounter
			else:
				output = [(outputLog, tempDir) for success, outputLog, tempDir in results]
				self.__processRepeats(measures, output)

			result = measures.endConfiguration()

			if success:
				outputFilePath = os.path.join(self.__outputDir, self.__inputFileName + '-resultConfig' + str(configurationCounter) + '.xml')
				print '* Writing configuration result XML to file %s ' % outputFilePath			
				outputFile = open(outputFilePath, 'w')
				outputFile.write(result)
				outputFile.close()
			
				measures.savePartialResults(os.path.join(configurationDir, 'partialResults.txt'))
				
				print '* Finished configuration %s. Running time: %s' % (configurationCounter, TimeFormatter.formatTime(time.time() - startTime))
				print ''
				sys.stdout.flush()
				
			configurationCounter = configurationCounter + 1
			
		print '' 
		sys.stdout.flush()
			
		#Removing running directory if not must be maintained
		if not self.__debug:
			shutil.rmtree(self.__workingDir)
			
	def __processRepeats(self, measures, output):
		args = []
		pool = multiprocessing.Pool(processes=self.__processes)
		for outputLog, tempDir in output:
			data = measures.getData(tempDir, outputLog)
			args.append(data);
		
		results = pool.map(process, args)
			
		measures.repeatsProcessed(results)
	        
	def perform(self, processing):
		if not processing:
			self.__run()
		else:
			self.__processOutput()
		
def __runExperiment(outputDir, configDir, inputFile, debug, workingDir, processing, processes): 
	e = Experiment(configDir, inputFile, outputDir, debug, workingDir, processing, processes)
	e.perform(processing)
		
def main():
	
	print '****************************************************'
	print '            Experimentation environment               '
	print ''
	print '****************************************************'
	
	parser = OptionParser()
	parser.add_option("-c", "--configDir", dest="configDir", help="experiment configuration directory")
	parser.add_option("-i", "--inputFile", dest="inputFile", help="experiment configuration file")
	parser.add_option("-o", "--outputDir", dest="outputDir", help="experiment results output directory", default='/tmp')
	parser.add_option("-w", "--workingDir", dest="workingDir", help="directory to store simulation results", default='/tmp')
	parser.add_option("-d", "--debug", dest="debug", help="preserve working directory output", action="store_true", default=False)
	parser.add_option("-p", "--processDir", dest="processDir", help="process output directory")
	parser.add_option("-P", "--processes", dest="processes", help="max number of parallel processes", default=multiprocessing.cpu_count())
	
	(options, args) = parser.parse_args()
	
	if not options.processDir is None:
		inputFile = None
		for file in os.listdir(options.processDir):
			if not os.path.isdir(file) and '.xml' in file:
				inputFile = file
		
		if inputFile is None:
			print 'ERROR: Experiment configuration file not found in output directory'
			sys.exit()
			
		__runExperiment(options.outputDir, options.processDir, inputFile, True, options.processDir, True, int(options.processes))
	else:
		if options.configDir is None or options.inputFile and None:
			parser.print_usage()
		else:				
			tmpDir = os.path.join(options.workingDir, 'experiment-' + options.inputFile + '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
			__runExperiment(options.outputDir, options.configDir, options.inputFile, options.debug, tmpDir, False, int(options.processes))

if __name__ == '__main__':
    main()
