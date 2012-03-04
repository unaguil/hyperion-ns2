from measures.generic.Overhead import Overhead as Overhead

from measures.dissemination.SentTableMessages import SentTableMessages as SentTableMessages
from measures.multicast.SentSearchMessages import SentSearchMessages as SentSearchMessages
from measures.multicast.SentSearchResponseMessages import SentSearchResponseMessages as SentSearchResponseMessages
from measures.multicast.SentRemoveRouteMessages import SentRemoveRouteMessages as SentRemoveRouteMessages
from measures.multicast.SentRemoveParametersMessages import SentRemoveParametersMessages as SentRemoveParametersMessages
from measures.multicast.SentRemoteMulticastMessages import SentRemoteMulticastMessages as SentRemoteMulticastMessages

class GraphcreationOverhead(Overhead):
	def __init__(self, period, simulationTime):		
		Overhead.__init__(self, period, simulationTime)
		
		self.addMeasure(SentTableMessages(period, simulationTime))
		self.addMeasure(SentSearchMessages(period, simulationTime))
		self.addMeasure(SentSearchResponseMessages(period, simulationTime))
		self.addMeasure(SentRemoveRouteMessages(period, simulationTime))
		self.addMeasure(SentRemoveParametersMessages(period, simulationTime))		
		self.addMeasure(SentRemoveParametersMessages(period, simulationTime))
		self.addMeasure(SentRemoteMulticastMessages(period, simulationTime))
		
		
