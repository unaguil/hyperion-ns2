from measures.generic.TrafficOverhead import TrafficOverhead as TrafficOverhead

class GraphcreationTrafficOverhead(TrafficOverhead):
	def __init__(self, period, simulationTime):		
		measures = ('dissemination.newProtocol.message.TableMessage', 
				   'multicast.search.message.SearchMessage', 
				   'multicast.search.message.SearchResponseMessage',
				   'multicast.search.message.RemoveRouteMessage',
				   'multicast.search.message.RemoveParametersMessage',
				   'multicast.search.message.RemoteMulticastMessage')
		
		TrafficOverhead.__init__(self, period, simulationTime, measures)
				
		
		
