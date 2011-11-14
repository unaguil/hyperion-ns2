from measures.generic.BroadcastedXXXPackets import BroadcastedXXXPackets

class SentACKMessages(BroadcastedXXXPackets):
	"""Total number of sent ACK messages"""
	
	def __init__(self, period, simulationTime):
		BroadcastedXXXPackets.__init__(self, 'peer.message.ACKMessage', period, simulationTime)