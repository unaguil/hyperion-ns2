from measures.multicast.SentRemoteXXXMessages import SentRemoteXXXMessages

class SentRemovedServicesMessages(SentRemoteXXXMessages):
	"""Total number of sent inhibed messages"""
	
	def __init__(self, period, simulationTime):
		SentRemoteXXXMessages.__init__(self, 'graphcreation.collisionbased.message.RemovedServicesMessage', period, simulationTime)
		
