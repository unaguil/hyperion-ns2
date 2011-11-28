from measures.multicast.SentRemoteXXXMessages import SentRemoteXXXMessages

class SentDisconnectServicesMessages(SentRemoteXXXMessages):
	"""Total number of sent disconnect services messages"""
	
	def __init__(self, period, simulationTime):
		SentRemoteXXXMessages.__init__(self, 'graphcreation.collisionbased.message.DisconnectServicesMessage', period, simulationTime)
		
