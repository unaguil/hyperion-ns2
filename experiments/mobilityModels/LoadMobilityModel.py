import os
import sys

MAX_SCENARIOS = 4

DELTA_TIME = 0.5

class LoadMobilityModel:
    def __init__(self, entries):
        self.__rotate = True
        
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "nNodes":
                self.__nNodes = int(value)
            if key == "finishTime":
                self.__finishTime = float(value) + DELTA_TIME 
            if key == "gridW":
                self.__maxX = int(value)
            if key == "gridH":
                self.__maxY = int(value)
            if key == "minSpeed":
                self.__minSpeed = float(value)
            if key == "maxSpeed":
                self.__maxSpeed = float(value)
            if key == "pauseTime":
                self.__pauseTime = float(value)
            if key == "rotate":
                self.__rotate = eval(value)
        
    def generate(self, workingDir, outputFile, repeat, strBuffer):        
        if self.__rotate:
            numScenario = repeat % MAX_SCENARIOS
        else:
            numScenario = 0
            
        mobilityFile = 'mobility-%d-%.1f-%d-%d-%.2f-%.2f-%.1f-%d.txt' % (self.__nNodes, self.__finishTime, self.__maxX, self.__maxY, self.__minSpeed, self.__maxSpeed, self.__pauseTime, numScenario)
        relativePath = 'mobilityScenarios/' + mobilityFile
        strBuffer.writeln('Using mobility scenario %s' % relativePath)
        absolutePath = os.path.abspath(relativePath)
        if not os.path.exists(absolutePath):
            strBuffer.writeln('ERROR: Mobility file %s not found' % relativePath)
            print strBuffer.getvalue()
            sys.exit()
        return absolutePath
