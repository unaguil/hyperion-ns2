from measures.dissemination.SentUpdateTableXXXMessages import SentUpdateTableXXXMessages

class SentCollisionResponseMessages(SentUpdateTableXXXMessages):
	"""Total number of sent collision response messages"""
	
	def __init__(self, period, simulationTime):
		SentUpdateTableXXXMessages.__init__(self, 'graphcreation.collisionbased.message.CollisionResponseMessage', period, simulationTime)
		
