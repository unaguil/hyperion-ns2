from measures.generic.SentPayloadXXXMessages import SentPayloadXXXMessages

class SentConnectServicesMessages(SentPayloadXXXMessages):
	"""Total number of sent connect services messages"""
	
	def __init__(self, period, simulationTime):
		SentPayloadXXXMessages.__init__(self, 'graphcreation.collisionbased.message.ConnectServicesMessage', period, simulationTime)
		
