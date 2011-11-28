from measures.generic.SentPayloadXXXMessages import SentPayloadXXXMessages

class SentCollisionMessages(SentPayloadXXXMessages):
	"""Total number of sent collision messages"""
	
	def __init__(self, period, simulationTime):
		SentPayloadXXXMessages.__init__(self, 'graphcreation.collisionbased.message.CollisionMessage', period, simulationTime)
		
