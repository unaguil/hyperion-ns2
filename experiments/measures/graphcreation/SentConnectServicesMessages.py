from measures.multicast.SentRemoteXXXMessages import SentRemoteXXXMessages

class SentConnectServicesMessages(SentRemoteXXXMessages):
	"""Total number of sent connect services messages"""
	
	def __init__(self, period, simulationTime):
		SentRemoteXXXMessages.__init__(self, 'graphcreation.collisionbased.message.ConnectServicesMessage', period, simulationTime)
		
