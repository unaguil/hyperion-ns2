import math
import StringIO

def printScenarioInfo(nNodes, transmissionRange, gridW, gridH, simulationTime, discardTime, strBuffer): 
        simulationArea = gridW * gridH
        nDensity = nNodes / float(simulationArea)
        nCoverage = math.pi * transmissionRange**2

        footprint = (nCoverage / simulationArea) * 100.0
        if footprint > 100.0:
            footprint = 100.0

        coveredRatio = footprint * nNodes
        if coveredRatio > 100.0:
            coveredRatio = 100.0

        maximumPath = math.sqrt(gridW**2 + gridH**2)
        networkDiameter = maximumPath / transmissionRange 
        neighborCount = nCoverage * nDensity
        if neighborCount > nNodes - 1:
            neighborCount = nNodes - 1;

        strBuffer.write('**************** Simulation parameters *********************\n')
        strBuffer.write('* Simulation time: %.2f s\n' % simulationTime)
        strBuffer.write('* Initial discarded time: %.2f s\n' % discardTime)
        strBuffer.write('* Simulation area: %.2f m x %.2f m = %.2f m^2\n' % (gridW, gridH, simulationArea))
        strBuffer.write('* Number of nodes: %d\n' % nNodes)
        strBuffer.write('* Node density: %.5f nodes/m^2\n' % nDensity)
        strBuffer.write('* Transmission range: %.2f m\n' % transmissionRange)
        strBuffer.write('* Node coverage: %.2f m^2\n' % nCoverage)
        strBuffer.write('* Footprint: %.2f %%\n' % footprint)
        strBuffer.write('* Covered ratio: %.2f %%\n' % coveredRatio)
        strBuffer.write('* Maximum path: %.2f m\n' % maximumPath)
        strBuffer.write('* Network diameter: %.2f hops\n' % networkDiameter)
        strBuffer.write('* Neighbor count: %.2f neighbors/node\n' % neighborCount)
        strBuffer.write('***********************************************************\n')


if __name__ == '__main__':
	nNodes = raw_input('Number of nodes: ')
	transmissionRange = raw_input('Transmission range: ')
	side = raw_input('Scenario side: ')

	strBuffer = StringIO.StringIO()
	printScenarioInfo(int(nNodes), float(transmissionRange), float(side), float(side), 0.0, 0.0, strBuffer)
	print strBuffer.getvalue()
