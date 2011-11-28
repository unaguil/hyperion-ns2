from measures.generic.SentPayloadXXXMessages import SentPayloadXXXMessages

class SentInhibeCollisionsMessages(SentPayloadXXXMessages):
	"""Total number of sent inhibed messages"""
	
	def __init__(self, period, simulationTime):
		SentPayloadXXXMessages.__init__(self, 'graphcreation.collisionbased.message.InhibeCollisionsMessage', period, simulationTime)
		
