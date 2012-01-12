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
    parameters = '-v 2 -n %s -s 1 -m %s -M %s -t %s -P 1 -p %s -x %s -y %s' % (nodes, minSpeed, maxSpeed, finishTime, pauseTime, gridW, gridH)
    
    paramList = [command]
                    
    for e in parameters.split('-'):
        paramList.append('-' + e)
    
    
    running = []
        
    for i in xrange(numScenarios):
        file = 'mobility-%s-%s-%s-%s-%s-%s-%s-%d.txt' % (str(nodes), str(finishTime), str(gridW), str(gridH), str(minSpeed), str(maxSpeed), str(pauseTime), i)
        outputFile = open(file, 'w') 
        print 'Output file %s' % file
        sys.stdout.flush()
    
        p = subprocess.Popen(paramList, stdout=outputFile)
        
        running.append((p, outputFile))
    
    for index, (p, outputFile) in enumerate(running):
        result = p.wait()
        outputFile.close()
            
        if result != 0:
            print "ERROR: There was a problem during mobility scenario %d generation" % (index + 1)
        else:
            print 'Scenario %d correctly generated' % (index + 1)
            
        sys.stdout.flush()
        
def main():    
    nodes = 70
    finishTime = 100.0
    gridW = 265
    gridH = 1058

    minSpeed = 0.001
    maxSpeed = 5.0
    pauseTime = 10.0
    
    numScenarios = 4
    
    generateNS2MobilityScenario(nodes, finishTime, gridW, gridH, minSpeed, maxSpeed, pauseTime, numScenarios)

if __name__ == '__main__':
    main()
