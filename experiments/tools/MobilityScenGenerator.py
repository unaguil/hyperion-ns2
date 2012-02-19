#!/usr/bin/python

import subprocess
import sys
from StringIO import StringIO

import ScenarioInfo

def generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, transmissionRange, numScenarios):

    print '' 
    print 'Generating %d scenarios' % numScenarios
    print '* Nodes:', nodes
    print '* FinishTime:', finishTime
    print '* Width', gridW
    print '* Height', gridH
    print '* MinSpeed', minSpeed
    print '* MaxSpeed', maxSpeed
    print '* PauseTime', pauseTime

    print ''

    strBuffer = StringIO()
    ScenarioInfo.printScenarioInfo(nodes, transmissionRange, gridW, gridH, finishTime, 0.0, strBuffer)
    print strBuffer.getvalue()
    strBuffer.close()
    
    command = './setdest'
    parameters = '-v 2 -n %d -s 1 -m %f -M %f -t %.1f -P 1 -p %s -x %d -y %d' % (nodes, minSpeed, maxSpeed, finishTime, pauseTime, gridW, gridH)
    
    cmd = command + ' ' + parameters
    
    paramList = [command]
                    
    for e in parameters.split('-'):
        paramList.append('-' + e)
    
    running = []
    
    files = []
        
    for i in xrange(numScenarios):
        print 'Generated using external command: %s' % cmd
        file = 'mobility-%d-%d-%d-%d-%.2f-%.2f-%d-%d.txt' % (nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, i)
        files.append(file)        
        outputFile = open(file, 'w') 
        print 'Output file %s' % file
        sys.stdout.flush()
    
        p = subprocess.Popen(paramList, stdout=outputFile)
        
        running.append((p, outputFile))
        
    outputFiles = []
    
    for index, (p, outputFile) in enumerate(running):
        result = p.wait()
        outputFile.close()
            
        if result != 0:
            print "ERROR: There was a problem during mobility scenario %d generation" % (index + 1)
        else:
            print 'Scenario %d correctly generated' % (index + 1)
            
        sys.stdout.flush()
        
    return files
        
def main():    
    nodes = 100
    finishTime = 300
    gridW = 700
    gridH = 700

    minSpeed = 0.00001
    maxSpeed = 10.0
    
    numScenarios = 20

    transmissionRange = 100.0
   
    for pauseTime in range(0, 10, 1000): 
        generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, transmissionRange, numScenarios)

if __name__ == '__main__':
    main()
