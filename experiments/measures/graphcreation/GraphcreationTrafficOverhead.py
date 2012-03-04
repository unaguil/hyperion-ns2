import re

from measures.generic.TrafficOverhead import TrafficOverhead as TrafficOverhead

class GraphcreationTrafficOverhead(TrafficOverhead):
	def __init__(self, period, simulationTime):
		patterns = []
					
		measures = ('dissemination.newProtocol.message.TableMessage', 
				   'multicast.search.message.SearchMessage', 
				   'multicast.search.message.SearchResponseMessage',
				   'multicast.search.message.RemoveRouteMessage',
				   'multicast.search.message.RemoveParametersMessage')	
		
		for measure in measures:
			pattern = "DEBUG .*?  - Peer .*? sending " + measure + " .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"
			patterns.append(re.compile(pattern))
			
		patterns.append(re.compile("DEBUG .*?  - Peer .*? sending multicast.search.message.RemoteMulticastMessage\(graphcreation.collisionbased.message.ConnectServicesMessage\) .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"))
		patterns.append(re.compile("DEBUG .*?  - Peer .*? sending multicast.search.message.RemoteMulticastMessage\(graphcreation.collisionbased.message.DisconnectServicesMessage\) .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"))
		patterns.append(re.compile("DEBUG .*?  - Peer .*? sending multicast.search.message.RemoteMulticastMessage\(graphcreation.collisionbased.message.RemovedServicesMessage\) .*? ([0-9]+) bytes ([0-9]+\,[0-9]+).*?"))
		
		TrafficOverhead.__init__(self, period, simulationTime, measures)
		
		self.setPatterns(patterns)
				
		
		
