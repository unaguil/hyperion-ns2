from AvgSearchTimeXXDiscoveredParameters import AvgSearchTimeXXDiscoveredParameters 

class AvgSearchTime25DiscoveredParameters(AvgSearchTimeXXDiscoveredParameters):	
	def __init__(self, period, simulationTime):		
		AvgSearchTimeXXDiscoveredParameters.__init__(self, period, simulationTime, 0.25) 
	