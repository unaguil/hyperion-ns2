from measures.generic.Overhead import Overhead as Overhead

from measures.multicast.SentRemoteMulticastYYYMessages import SentRemoteMulticastYYYMessages as SentRemoteMulticastYYYMessages

class GraphsearchOverhead(Overhead):
	def __init__(self, period, simulationTime):		
		Overhead.__init__(self, period, simulationTime)
				
		self.addMeasure(SentRemoteMulticastYYYMessages(period, simulationTime, 'graphsearch.forward.message.FCompositionMessage'))
		
		self.addMeasure(SentRemoteMulticastYYYMessages(period, simulationTime, 'graphsearch.backward.message.BCompositionMessage'))
		
		self.addMeasure(SentRemoteMulticastYYYMessages(period, simulationTime, 'graphsearch.bidirectionalsearch.message.CompositionNotificationMessage'))
		
		
