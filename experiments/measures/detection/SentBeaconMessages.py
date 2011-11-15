from measures.generic.BroadcastedXXXPackets import BroadcastedXXXPackets

class SentBeaconMessages(BroadcastedXXXPackets):
	"""Total number of sent beacon messages"""
	
	def __init__(self, period, simulationTime):
		BroadcastedXXXPackets.__init__(self, 'detection.message.BeaconMessage', period, simulationTime)