from measures.generic.GenericMeasure import GenericMeasure

import measures.generic.Units as Units

class NewNeighborsDetected(GenericMeasure):
	"""Total number of new neighbors which are detected"""
	
	def __init__(self, period, simulationTime):
		GenericMeasure.__init__(self, r"DEBUG detection.beaconDetector.BeaconDetector  - Peer [0-9]* has new neighbors:.*?([0-9]+\,[0-9]+).*?", period, simulationTime, Units.NEIGHBORS)

	def parseLine(self, line):
		self.parseInc(line)
		