import sys
import subprocess
from time import time

import util.TimeFormatter as TimeFormatter

class RandomWaypoint:
    
    def __init__(self, entries):
        for entry in entries:
            value = entry.firstChild.data
            key = entry.getAttribute("key")
            
            if key == "nNodes":
                self.__nNodes = value
            if key == "finishTime":
                self.__simTime = value
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
        
    def generate(self, workingDir, file, repeat, strBuffer):
        command = 'tools/setdest'
        parameters = '-v 2 -n %s -s 1 -m %s -M %s -t %s -P 1 -p %s -x %s -y %s' % (self.__nNodes, self.__minSpeed, self.__maxSpeed, self.__simTime, self.__pauseTime, self.__maxX, self.__maxY)
        
        cmd = command + ' ' + parameters
        
        strBuffer.writeln('')
        strBuffer.writeln('************* Random waypoint ****************')
        strBuffer.writeln('* Nodes: %s' % self.__nNodes)
        strBuffer.writeln('* Minimum speed: %s m/s' % self.__minSpeed)
        strBuffer.writeln('* Maximum speed: %s m/s' % self.__maxSpeed)
        strBuffer.writeln('* Simulation time: %s s' % self.__simTime)
        strBuffer.writeln('* Pause time: %s s' % self.__pauseTime)
        strBuffer.writeln('* Max X: %s m' % self.__maxX)
        strBuffer.writeln('* Max Y: %s m' % self.__maxY)
        
        strBuffer.writeln('* Generated using external command: %s' % cmd)
        
        paramList = [command]
                
        for e in parameters.split('-'):
            paramList.append('-' + e)
        
        startTime = time()
        
        oFilePath = workingDir + '/' + file
        outputFile = open(oFilePath, 'w')
        p = subprocess.Popen(paramList, stdout=outputFile)
        result = p.wait()
        outputFile.close()
        
        if result != 0:
            strBuffer.writeln('ERROR: There was a problem during mobility model generation')
            print strBuffer.getvalue()
            sys.exit()

        strBuffer.writeln('* Model generation time: %s' % TimeFormatter.formatTime(time() - startTime))
        
        strBuffer.writeln('**********************************************')
        
        return file 
