from measures.generic.ReceivedXXXPackets import ReceivedXXXPackets

class ReceivedBeaconMessages(ReceivedXXXPackets):
	"""Total number of received beacon messages"""
	
	def __init__(self, period, simulationTime):
		ReceivedXXXPackets.__init__(self, 'detection.message.BeaconMessage', period, simulationTime)
	