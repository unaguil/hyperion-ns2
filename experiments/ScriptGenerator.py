import xml.dom.minidom as minidom
import math
import os

from mobilityModels.MobilityModelGenerator import MobilityModelGenerator
from populators.PopulatorGenerator import PopulatorGenerator
from nodeBehavior.NodeBehaviorGenerator import NodeBehaviorGenerator
from tools import ScenarioInfo

DELTA_TIME = 0.5

class ScriptGenerator:
	def __init__(self, config, strBuffer):
		scriptConfig = minidom.parseString(config)
		self.__entries = scriptConfig.getElementsByTagName("entry")
		
		#Default transmission range (100 meters)
		self.__transmissionRange = 100
		
		for entry in self.__entries:
			value = entry.firstChild.data
			key = entry.getAttribute("key")
			if key == "nNodes":
				self.__nNodes = int(value)
			if key == "finishTime":
				self.__simulationTime = float(value)
				self.__finishTime = self.__simulationTime + DELTA_TIME
			if key == "gridW":
				self.__gridW = float(value)
			if key == "gridH":
				self.__gridH = float(value)
			if key == "javaAgent":
				self.__javaAgent = value
			if key == "transmissionRange":
				self.__transmissionRange = float(value)
			if key == "discardTime":
				self.__discardTime = float(value)

		ScenarioInfo.printScenarioInfo(self.getNNodes(), self.__transmissionRange, self.getGridW(), self.getGridH(), self.__simulationTime, self.__discardTime, strBuffer)
	
		codeTag = scriptConfig.getElementsByTagName("code")
		if len(codeTag) > 0:
			self.__codeFile = codeTag[0].getAttribute("codeFile")
		else:
			self.__codeFile = ''
		
	def generate(self, fileName, workingDir, repeat, strBuffer):
		#Use mobility model generator to create mobility model using script configuration
		mobilityModelGenerator = MobilityModelGenerator()
		mobilityModel = mobilityModelGenerator.generateModel(self.__entries) 
		
		#Create populator which includes population
		populatorGenerator = PopulatorGenerator()
		nodePopulator = populatorGenerator.generatePopulator(self.__entries)
		
		#Create node behavior generator
		behaviorGenerator = NodeBehaviorGenerator()
		nodeBehavior = behaviorGenerator.generateNodeBehavior(self.__entries, nodePopulator)
		
		if nodePopulator is not None:
			nodePopulator.generate(workingDir, strBuffer)
		
		filePath = os.path.join(workingDir, fileName)
		file = open(filePath, "w")
		file.write("source WCommon.tcl\n")
		file.write("\n")
		file.write("set nNodes " + str(self.__nNodes) + "\n")
		file.write("set finishTime " + str(self.__finishTime) + "\n")
		file.write("set gridW " + str(self.__gridW) + "\n")
		file.write("set gridH " + str(self.__gridH) + "\n")
		file.write("set javaAgent " + self.__javaAgent + "\n")
		file.write("\n")
		file.write("set ns_		[new Simulator]\n")
		file.write("set tracefd     [open simple.tr w]\n")
		file.write("$ns_ trace-all $tracefd\n")
		file.write("proc do_something {agents_ nodes_ god_} {\n")
		file.write("\tglobal ns_ finishTime\n")
		file.write("\tupvar $agents_ agents\n")
		file.write("\tupvar $nodes_ node_\n")
		file.write("\n")
		
		if self.__codeFile is not '':
			#Write code
			codeFilePath = os.path.join(workingDir, self.__codeFile)
			codeFile = open(codeFilePath, 'r')
			code = codeFile.read()
			file.write(code)
		
		if mobilityModel is not None:
			file.write('\n')
			mobilityFilePath = mobilityModel.generate(workingDir, 'mobility-scenario.txt', repeat, strBuffer)
			file.write('\tsource ' + mobilityFilePath + '\n')
			
		if nodeBehavior is not None:
			file.write('\n')
			nodeBehaviorPath = os.path.join(workingDir, 'nodeBehavior.txt')
			oFile = open(nodeBehaviorPath, 'w')
			nodeBehavior.generate(workingDir, oFile, strBuffer)
			oFile.close()
			file.write('\tsource nodeBehavior.txt\n')
		
		file.write("}\n")
		file.write("\n")
		file.write("wireless_simulation_extended $nNodes $finishTime $javaAgent true $gridW $gridH 100 OFF\n")
		file.close()
			
	def getGridW(self):
		return self.__gridW
	
	def getGridH(self):
		return self.__gridH
	
	def getNNodes(self):
		return self.__nNodes
	
	def getTransmissionRange(self):
		return self.__transmissionRange
	
