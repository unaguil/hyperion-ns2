from AvgSearchTimeXXDiscoveredParameters import AvgSearchTimeXXDiscoveredParameters 

class AvgSearchTime100DiscoveredParameters(AvgSearchTimeXXDiscoveredParameters):	
	def __init__(self, period, simulationTime):		
		AvgSearchTimeXXDiscoveredParameters.__init__(self, period, simulationTime, 1.0) 
	