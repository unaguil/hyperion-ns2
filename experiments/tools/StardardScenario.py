#!/usr/bin/python

import math
import sys

import MobilityScenGenerator
import DrawScenario

def getNodes(anp, asp_hops, w1, w2, w3):
	return math.exp(w1) * math.pow(anp, w2) * math.pow(asp_hops, w3)

def getArea(anp, asp_hops, w1, w2, w3):
	return math.exp(w1) * math.pow(anp, w2) * math.pow(asp_hops, w3)

def main():
	print '**********************************************************'
	print '            Standard scenario generator'
	print '**********************************************************'
	
	anp = float(raw_input('Average Network Partitioning ANP: '))
	if anp < 0.0 or anp > 1.0:
		print 'ANP (Average Network Partitioning is a percentage ratio [0-1]'
		sys.exit()
	
	asp_hops = float(raw_input('Average Shortest Path Hops: '))
	if asp_hops < 0:
		print 'Average Shortest Path Hops must be positive'
		sys.exit()
	
	print ''
	print ''
	    
	print 'Generating scenario with ANP = %.2f and ASPhops = %d' % (anp, asp_hops)
	
	nodes, area, width_R = generateScenario(anp, asp_hops)
	
	print 'Nodes: %d' % nodes
	print 'Area: %.2f R^2' % (area)
	print 'Width: %.2f R' % width_R
	
	################# generate scenarios
	transmissionRange = 100
	
	width = width_R * transmissionRange
	
	outputFiles = MobilityScenGenerator.generateNS2MobilityScenario(nodes, 100.0, width, width, 0.000001, 0.000001, 200.0, 1)
	
	#for outputFile in outputFiles:
	#	DrawScenario.drawScenario(outputFile, outputFile + '.png', width, width)
		
def generateScenario(anp, asp_hops):
	node_exps = [-0.164, -0.417, 2.468]
	area_exps = [0.567, -0.0769, 2.159]
	
	nodes = getNodes(anp, asp_hops, *node_exps)
	area = getArea(anp, asp_hops, *area_exps)
	
	side = math.sqrt(area)
	
	return math.ceil(nodes), area, round(side)
	
if __name__ == '__main__':
	main()

