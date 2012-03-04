from measures.generic.SentXXXMessages import SentXXXMessages

class SentRemoteMulticastMessages(SentXXXMessages):	
	def __init__(self, period, simulationTime):
		SentXXXMessages.__init__(self, 'multicast.search.message.RemoteMulticastMessage', period, simulationTime)
		
