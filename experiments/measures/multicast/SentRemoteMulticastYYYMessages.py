from measures.generic.SentXXXYYYMessages import SentXXXYYYMessages

class SentRemoteMulticastYYYMessages(SentXXXYYYMessages):	
	def __init__(self, period, simulationTime, payloadClass):
		SentXXXYYYMessages.__init__(self, 'multicast.search.message.RemoteMulticastMessage', payloadClass, period, simulationTime)
		
