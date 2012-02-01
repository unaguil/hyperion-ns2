#!/usr/bin/python

import subprocess
import sys

def generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, numScenarios):
    
    print 'Generating %d ', numScenarios
    print '\tNodes:', nodes
    print '\tFinishTime:', finishTime
    print '\tWidth', gridW
    print '\tHeight', gridH
    print '\tMinSpeed', minSpeed
    print '\tMaxSpeed', maxSpeed
    print '\tPauseTime', pauseTime
    
    command = './setdest'
    parameters = '-v 1 -n %s -M %f -t %.1f -p %s -x %s -y %s' % (nodes, maxSpeed, finishTime, pauseTime, gridW, gridH)
    
    cmd = command + ' ' + parameters
    
    print 'Generated using external command: %s' % cmd
    
    paramList = [command]
                    
    for e in parameters.split('-'):
        paramList.append('-' + e)
    
    running = []
    
    files = []
        
    for i in xrange(numScenarios):
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
    gridW = 1500
    gridH = 1300

    minSpeed = 0.0
    maxSpeed = 10.0
    pauseTime = 1000.0
    
    numScenarios = 20
    
    generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, numScenarios)

if __name__ == '__main__':
    main()
