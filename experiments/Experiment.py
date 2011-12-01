#!/usr/bin/python

import sys
import os
import shutil
import subprocess
import math
import re
import threading
import time
import datetime
import multiprocessing

import util.StrBuffer as StrBuffer

from optparse import OptionParser

from ConfigGenerator import ConfigGenerator
from measures.Measures import Measures
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
						print '* ERROR: JVM failed during simulation. Killing process. See ' + self.__tempDir + '/' + file
						self.__process.kill()
						return							
			except OSError:
				pass
			
			time.sleep(self.__period)
		
	def cancel(self):
		self.__stop = True

class RepeatRunner:
	def __init__(self, tempDir, config, workingDir, inputFile, configGenerator, repeat, repeatNumber):
		self.__tempDir = tempDir
		self.__config = config
		self.__configDir = workingDir
		self.__inputFile = inputFile
		self.__configGenerator = configGenerator
		self.__repeat = repeat
		self.__repeatNumber = repeatNumber
		
		self.__try = 1 
		
	def __execute(self):
		strBuffer = StrBuffer.StrBuffer()
		strBuffer.writeln('')
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
						
		scriptGenerator = ScriptGenerator(self.__config, self.__inputFile, strBuffer)
		scriptGenerator.generate('Script.tcl', self.__tempDir, self.__repeat, strBuffer)
		
		#Run script
		simStartTime = time.time()
		out = open(self.__tempDir + '/out', 'w')
		err = open(self.__tempDir + '/err', 'w')
		
		strBuffer.writeln('* Launching simulation script on directory %s try %d' % (self.__tempDir, self.__try))
		print strBuffer.getvalue()
		sys.stdout.flush()
		
		self.__p = subprocess.Popen(['ns', 'Script.tcl'], stdout=out, stderr=err, cwd=self.__tempDir)
		
		self.__timer = JVMCheckingTimer(JVM_DUMP_CHECK_TIME, self.__p, self.__tempDir) 
		self.__timer.start()
		result = self.__p.wait()
		self.__timer.cancel()
		
		out.close()
		err.close()
		
		if result != 0:
			print '* ERROR: There was a problem during simulation execution on directory %s' % self.__tempDir
			sys.stdout.flush()
			return False
		
		print '* NS-2 simulation on directory %s running time: %s\n\n' % (self.__tempDir, TimeFormatter.formatTime(time.time() - simStartTime))
		sys.stdout.flush()
		
		self.__compressOutputLog()
		
		return True
	
	def terminate(self):
		self.__p.kill()
		self.__timer.cancel()
		
	def run(self):
		success = False
		while self.__try <= MAX_TRIES and not success:		
			success = self.__execute()
			self.__try += 1
			
		if not success:
			print '* ERROR: Max tries for simulation execution reached'
			return False
		else:
			return True
			
	def __compressOutputLog(self):  
		startTime = time.time()
		print '* Compressing output log file %s' % self.__getPlainLog()
		p = subprocess.Popen(['gzip', self.__getPlainLog()])
		result = p.wait()
		
		if result != 0:
			print 'ERROR: There was a problem compressing file %s' % self.__getPlainLog()
			sys.stdout.flush()
			return False
		
		print '* Compressed log obtained in %s time: %s' % (self.getOutputLog(), TimeFormatter.formatTime(time.time() - startTime)) 
		print ''
		return True
	
	def __getPlainLog(self):
		return self.__tempDir + '/output.log'
	
	def getOutputLog(self):
		return self.__tempDir + '/output.log.gz'
	
	def __prepareSimulationFiles(self, tempDir, config, workingDir):
		configFile = open(tempDir + '/Configuration.xml', 'w')
		configFile.write(config)
		configFile.close()
		
		shutil.copy2('./common/WCommon.tcl', tempDir + '/WCommon.tcl')
		
		shutil.copy2('log4j.properties', tempDir + '/log4j.properties')
		
		#Copy all files contained in input directory to temporal directory
		for file in os.listdir(workingDir):
			srcPath = workingDir + '/' + file
			dstPath = tempDir + '/' + file
			if not os.path.isdir(srcPath):
				shutil.copy2(srcPath, dstPath)
				
def runRepeat(args):
	try:
		repeatDir, config, configDir, inputFile, configGenerator, counter, repeatNumber = args
				
		r = RepeatRunner(repeatDir, config, configDir, inputFile, configGenerator, counter, repeatNumber)
		return (not r.run(), r.getOutputLog())
	except KeyboardInterrupt:
		print '* Terminating process'
		r.terminate()

class Experiment:
	def __init__(self, configDir, inputFile, outputDir, debug, workingDir, processing):
		self.__configDir = configDir
		self.__outputDir = outputDir
		self.__inputFileName = inputFile
		self.__inputFile = self.__configDir + '/' + inputFile
		self.__debug = debug
		self.__workingDir = workingDir
		
		if not processing and os.path.isdir(self.__workingDir):
			shutil.rmtree(self.__workingDir)
		
		if not processing:	
			os.mkdir(self.__workingDir)
		
			shutil.copy2(self.__inputFile, self.__workingDir + '/')
			
	def __saveTimestamp(self, dir):
		oFile = open(dir + '/launched.txt', 'w')
		oFile.write("Experiment started on: %s " % datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
		oFile.close()

	def __run(self):		
		configGenerator = ConfigGenerator(self.__inputFile)
		
		measures = Measures(self.__inputFile)
		
		initTime = time.time()
		
		error = False

		configurationCounter = 0		
		
		self.__saveTimestamp(self.__workingDir)
		
		while configGenerator.hasNext():
			configurationDir = self.__workingDir + '/configuration-' + str(configurationCounter)
			
			os.mkdir(configurationDir)
			
			startTime = time.time()
			
			repeatNumber = configGenerator.getRepeat()
			
			print ''
			print "* Running experiment configuration %d with %d repetition(s)" % (configurationCounter + 1, repeatNumber)
			print ''
			sys.stdout.flush() 
			#Get current execution configuration
			config, generatedExpConfig = configGenerator.next()
			measures.startConfiguration(configurationCounter, configGenerator.getTag(), configGenerator.getType(), configGenerator.getSimulationTime(), configGenerator.getDiscardTime())
			
			#save current configuration
			generatedConfigFile = open(configurationDir + '/GeneratedConfig.xml' , 'w')
			generatedConfigFile.write(generatedExpConfig)
			generatedConfigFile.close()						
			
			data = []
			
			for counter in range(repeatNumber):		
				repeatDir = configurationDir + '/repeat-' + str(counter)
				data.append((repeatDir, config, self.__configDir, self.__inputFile, configGenerator, counter, repeatNumber))
				
			pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
			results = pool.map(runRepeat, data) 

			print '* Finalizing configuration. Parsing output log files'
			print ''
			sys.stdout.flush()
			
			outputLogs = [outputLog for error, outputLog in results]
			
			self.__processRepeat(measures, outputLogs)

			result = measures.endConfiguration()

			outputFilePath = self.__outputDir + '/' + self.__inputFileName + '-resultConfig' + str(configurationCounter) + '.xml'
			print '* Writing configuration result to file %s ' % outputFilePath			
			outputFile = open(outputFilePath, 'w')
			outputFile.write(result)
			
			measures.savePartialResults(configurationDir + '/partialResults.txt')
				
			print '* Configuration execution time: %s' % TimeFormatter.formatTime(time.time() - startTime)
			print ''
			sys.stdout.flush()
			
			configurationCounter = configurationCounter + 1
			
		experimentTime = time.time() - initTime 
			
		if error:
			print 'Experiment finished with errors. Total time: %s' % TimeFormatter.formatTime(experimentTime)
		else:
			print 'Experiment finished. Total time: %s' % TimeFormatter.formatTime(experimentTime)
						
		print '' 
		sys.stdout.flush()
			
		#Removing running directory if not must be maintained
		if not self.__debug:
			shutil.rmtree(self.__workingDir)	
		
	def __processRepeat(self, measures, outputLogs):
		for outputLog in outputLogs:
			print '* Output log %s file size %s' % (outputLog, self.__sizeof_fmt(os.path.getsize(outputLog)))
			sys.stdout.flush()
			#Measure results
			logProcessStartTime = time.time()
			measures.startRepeat()
			measures.parseLog(outputLog)
			measures.endRepeat()
							
			print '* Output log %s parsing time: %s' % (outputLog, TimeFormatter.formatTime(time.time() - logProcessStartTime))
			print ''
			sys.stdout.flush()
		
	def __sizeof_fmt(self, num):
	    for x in ['bytes','KB','MB','GB','TB']:
	        if num < 1024.0:
	            return "%3.1f%s" % (num, x)
	        num /= 1024.0		
	        
	def __processOutput(self):
		configGenerator = ConfigGenerator(self.__inputFile)
		
		measures = Measures(self.__inputFile)
		
		initTime = time.time()

		configurationCounter = 0		
		while configGenerator.hasNext():
			configurationDir = self.__workingDir + '/configuration-' + str(configurationCounter)
			
			startTime = time.time()
			
			repeatNumber = configGenerator.getRepeat()
			
			print ''
			print ''
			print "* Processing experiment configuration %d output with %d repetition(s)" % (configurationCounter + 1, repeatNumber)
			sys.stdout.flush() 
			#Get current execution configuration
			config = configGenerator.next()
			measures.startConfiguration(configurationCounter, configGenerator.getType())
			
			scriptGenerator = ScriptGenerator(config, self.__inputFile)

			print ''
			print 'Parsing output log files'
			sys.stdout.flush()
			outputLogs = []
			
			for i in range(repeatNumber):
				outputLog = configurationDir + '/repeat-' + str(i) + '/output.log.gz'
				outputLogs.append(outputLog)
			
			self.__processRepeat(measures, outputLogs)

			measures.endConfiguration(configurationCounter)
			
			configurationCounter = configurationCounter + 1
			
			print '* Configuration processing time: %s' % TimeFormatter.formatTime(time.time() - startTime)
			print ''
			sys.stdout.flush()

		experimentTime = time.time() - initTime

		print 'Experiment output processing finished. Total time: %s' % TimeFormatter.formatTime(experimentTime)
		print '' 
		
		results =  measures.getXMLResults(scriptGenerator.getDiscardTime(), experimentTime, configGenerator.getTag(), configGenerator.getType())
		
		#Save results
		for item in results.items():
			
			self.__outputDir.write(results)
		
	def perform(self, processing):
		if not processing:
			self.__run()
		else:
			self.__processOutput()
		
def __runExperiment(outputDir, configDir, inputFile, debug, workingDir, processing): 
	e = Experiment(configDir, inputFile, outputDir, debug, workingDir, processing)
	e.perform(processing)
		
def main():
	
	print '****************************************************'
	print '            Experimentation environment               '
	print ''
	print '****************************************************'
	
	parser = OptionParser()
	parser.add_option("-c", "--configDir", dest="configDir", help="experiment configuration directory")
	parser.add_option("-f", "--file", dest="inputFile", help="experiment configuration file")
	parser.add_option("-o", "--output", dest="outputDir", help="experiment results output directory", default='/tmp')
	parser.add_option("-w", "--workingDir", dest="workingDir", help="directory to store simulation results")
	parser.add_option("-d", "--debug", dest="debug", help="preserve working directory output", action="store_true", default=False)
	parser.add_option("-p", "--processDir", dest="processDir", help="process output directory")
	
	(options, args) = parser.parse_args()
	
	if not options.processDir is None:
		inputFile = None
		for file in os.listdir(options.processDir):
			if not os.path.isdir(file) and '.xml' in file:
				inputFile = file
		
		if inputFile is None:
			print 'ERROR: Experiment config file not found in output directory'
			sys.exit()
			
		__runExperiment(options.outputDir, options.processDir, inputFile, True, options.processDir, True)
	else:
		if options.configDir is None or options.inputFile and None:
			parser.print_usage()
		else:				
			if options.workingDir is None:
				workingDir = '/tmp/experiment-' + options.inputFile
			else:
				workingDir = options.workingDir
			
			__runExperiment(options.outputDir, options.configDir, options.inputFile, options.debug, workingDir, False)

if __name__ == '__main__':
    main()
