from measures.generic.SentPayloadXXXMessages import SentPayloadXXXMessages

class SentForwardMessages(SentPayloadXXXMessages):
	"""Total number of sent forward messages"""
	
	def __init__(self, period, simulationTime):
		SentPayloadXXXMessages.__init__(self, 'graphcreation.collisionbased.message.ForwardMessage', period, simulationTime)
		
