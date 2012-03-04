import re

from measures.generic.TrafficOverhead import TrafficOverhead as TrafficOverhead

class GraphsearchTrafficOverhead(TrafficOverhead):
	def __init__(self, period, simulationTime):
		patterns = []	
		patterns.append(re.compile("DEBUG .*?  - Peer .*? sending multicast.search.message.RemoteMulticastMessage\(graphsearch.forward.message.FCompositionMessage\) .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"))
		patterns.append(re.compile("DEBUG .*?  - Peer .*? sending multicast.search.message.RemoteMulticastMessage\(graphsearch.backward.message.BCompositionMessage\) .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"))
		patterns.append(re.compile("DEBUG .*?  - Peer .*? sending multicast.search.message.RemoteMulticastMessage\(graphsearch.bidirectionalsearch.message.CompositionNotificationMessage\) .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"))
		
		TrafficOverhead.__init__(self, period, simulationTime, [])
		
		self.setPatterns(patterns)
				
		
		
