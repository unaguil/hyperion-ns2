from measures.generic.ReceivedXXXPackets import ReceivedXXXPackets

class ReceivedACKMessages(ReceivedXXXPackets):
	"""Total number of received ACK messages"""
	
	def __init__(self, period, simulationTime):
		ReceivedXXXPackets.__init__(self, 'peer.message.ACKMessage', period, simulationTime)
	