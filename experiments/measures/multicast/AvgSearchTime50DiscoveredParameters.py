from AvgSearchTimeXXDiscoveredParameters import AvgSearchTimeXXDiscoveredParameters 

class AvgSearchTime50DiscoveredParameters(AvgSearchTimeXXDiscoveredParameters):	
	def __init__(self, period, simulationTime):		
		AvgSearchTimeXXDiscoveredParameters.__init__(self, period, simulationTime, 0.50) 
	