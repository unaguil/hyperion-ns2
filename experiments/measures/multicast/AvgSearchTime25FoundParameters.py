from AvgSearchTimeXXFoundParameters import AvgSearchTimeXXFoundParameters 

class AvgSearchTime25FoundParameters(AvgSearchTimeXXFoundParameters):	
	def __init__(self, period, simulationTime):		
		AvgSearchTimeXXFoundParameters.__init__(self, period, simulationTime, 0.25) 
	