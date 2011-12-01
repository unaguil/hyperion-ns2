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
                self.__nNodes = value
            if key == "finishTime":
                self.__finishTime = float(value) + DELTA_TIME 
            if key == "gridW":
                self.__maxX = value
            if key == "gridH":
                self.__maxY = value
            if key == "minSpeed":
                self.__minSpeed = value
            if key == "maxSpeed":
                self.__maxSpeed = value
            if key == "pauseTime":
                self.__pauseTime = value
            if key == "rotate":
                self.__rotate = eval(value)
        
    def generate(self, workingDir, outputFile, repeat, strBuffer):        
        if self.__rotate:
            numScenario = repeat % MAX_SCENARIOS
        else:
            numScenario = 0
            
        mobilityFile = 'mobility-%s-%.1f-%s-%s-%s-%s-%s-%d.txt' % (str(self.__nNodes), self.__finishTime, str(self.__maxX), str(self.__maxY), str(self.__minSpeed), str(self.__maxSpeed), str(self.__pauseTime), numScenario)
        relativePath = 'mobilityScenarios/' + mobilityFile
        strBuffer.writeln('Using mobility scenario %s' % relativePath)
        absolutePath = os.path.abspath(relativePath)
        if not os.path.exists(absolutePath):
            strBuffer.writeln('ERROR: Mobility file %s not found' % relativePath)
            print strBuffer.getvalue()
            sys.exit()
        return absolutePath
