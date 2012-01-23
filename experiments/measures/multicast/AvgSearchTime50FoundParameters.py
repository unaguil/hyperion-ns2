from AvgSearchTimeXXFoundParameters import AvgSearchTimeXXFoundParameters 

class AvgSearchTime50FoundParameters(AvgSearchTimeXXFoundParameters):	
	def __init__(self, period, simulationTime):		
		AvgSearchTimeXXFoundParameters.__init__(self, period, simulationTime, 0.50) 
	