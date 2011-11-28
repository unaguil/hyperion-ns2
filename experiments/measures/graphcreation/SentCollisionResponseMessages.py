from measures.generic.SentPayloadXXXMessages import SentPayloadXXXMessages

class SentCollisionResponseMessages(SentPayloadXXXMessages):
	"""Total number of sent collision response messages"""
	
	def __init__(self, period, simulationTime):
		SentPayloadXXXMessages.__init__(self, 'graphcreation.collisionbased.message.CollisionResponseMessage', period, simulationTime)
		
