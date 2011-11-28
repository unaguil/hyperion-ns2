from measures.multicast.SentRemoteXXXMessages import SentRemoteXXXMessages

class SentForwardMessages(SentRemoteXXXMessages):
	"""Total number of sent forward messages"""
	
	def __init__(self, period, simulationTime):
		SentRemoteXXXMessages.__init__(self, 'graphcreation.collisionbased.message.ForwardMessage', period, simulationTime)
		
