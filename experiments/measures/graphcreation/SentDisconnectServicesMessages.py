from measures.generic.SentPayloadXXXMessages import SentPayloadXXXMessages

class SentDisconnectServicesMessages(SentPayloadXXXMessages):
	"""Total number of sent disconnect services messages"""
	
	def __init__(self, period, simulationTime):
		SentPayloadXXXMessages.__init__(self, 'graphcreation.collisionbased.message.DisconnectServicesMessage', period, simulationTime)
		
