#!/usr/bin/python

import subprocess
import sys

def generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, numScenarios):
    
    print 'Generating %d scenarios' % numScenarios
    print '\tNodes:', nodes
    print '\tFinishTime:', finishTime
    print '\tWidth', gridW
    print '\tHeight', gridH
    print '\tMinSpeed', minSpeed
    print '\tMaxSpeed', maxSpeed
    print '\tPauseTime', pauseTime
    
    command = './setdest'
    parameters = '-v 2 -n %s -s 1 -m %f -M %f -t %.1f -P 1 -p %s -x %s -y %s' % (nodes, 0.00001, maxSpeed, finishTime, pauseTime, gridW, gridH)
    
    cmd = command + ' ' + parameters
    
    paramList = [command]
                    
    for e in parameters.split('-'):
        paramList.append('-' + e)
    
    running = []
    
    files = []
        
    for i in xrange(numScenarios):
        print 'Generated using external command: %s' % cmd
        file = 'mobility-%s-%s-%s-%s-%s-%s-%s-%d.txt' % (str(nodes), str(finishTime), str(gridW), str(gridH), str(minSpeed), str(maxSpeed), str(pauseTime), i)
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
    finishTime = 1000.0
    gridW = 700
    gridH = 700

    minSpeed = 0.0
    maxSpeed = 10.0
    
    numScenarios = 20
   
    for pauseTime in range(0, 1200, 200): 
        generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, numScenarios)

if __name__ == '__main__':
    main()
