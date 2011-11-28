from measures.dissemination.SentUpdateTableXXXMessages import SentUpdateTableXXXMessages

class SentCollisionMessages(SentUpdateTableXXXMessages):
	"""Total number of sent collision messages"""
	
	def __init__(self, period, simulationTime):
		SentUpdateTableXXXMessages.__init__(self, 'graphcreation.collisionbased.message.CollisionMessage', period, simulationTime)
		
