from measures.dissemination.SentUpdateTableXXXMessages import SentUpdateTableXXXMessages

class SentInhibeCollisionsMessages(SentUpdateTableXXXMessages):
	"""Total number of sent inhibed messages"""
	
	def __init__(self, period, simulationTime):
		SentUpdateTableXXXMessages.__init__(self, 'graphcreation.collisionbased.message.InhibeCollisionsMessage', period, simulationTime)
		
