from AvgSearchTimeXXFoundParameters import AvgSearchTimeXXFoundParameters 

class AvgSearchTime75FoundParameters(AvgSearchTimeXXFoundParameters):	
	def __init__(self, period, simulationTime):		
		AvgSearchTimeXXFoundParameters.__init__(self, period, simulationTime, 0.75) 
	