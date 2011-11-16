import xml.dom.minidom as minidom
from InterpolatedEntry import InterpolatedEntry

class ConfigGenerator:
	def __init__(self, expConfigFile):
		expConfig = minidom.parse(expConfigFile)
		experiment = expConfig.documentElement
		self.__tag = experiment.getAttribute('tag')
		self.__type = experiment.getAttribute('type') 
		
		staticConfig = expConfig.getElementsByTagName("staticConfig")		
		self.staticEntries = staticConfig[0].getElementsByTagName("entry")
		
		#Obtain the number of repetitions for each configuration
		repeatEntry = expConfig.getElementsByTagName("repeat")
		if len(repeatEntry) == 0:
			self.__repeat = 3
		else: 
			self.__repeat = int(repeatEntry[0].getAttribute("number"))
	
		self.interpolatedEntries = []

		dynamicEntries = expConfig.getElementsByTagName("dynamicEntry")
		if not dynamicEntries:
			self.interpolatedEntries.append(InterpolatedEntry('NONE', 'LinearInterpolator', 1, 1, 1))
		for dynamicEntry in dynamicEntries:
			key = dynamicEntry.getAttribute("key")
			interpolator = dynamicEntry.getAttribute("interpolator")
			start = int(dynamicEntry.getAttribute("start"))
			end = int(dynamicEntry.getAttribute("end"))
			step = int(dynamicEntry.getAttribute("step"))
			text = dynamicEntry.getAttribute("text")
			self.interpolatedEntries.append(InterpolatedEntry(key, interpolator, text, start, end, step))
			
		self.__measures = expConfig.getElementsByTagName("measure")
		
		self.__entries = expConfig.getElementsByTagName("entry")	
		for entry in self.__entries:
			value = entry.firstChild.data
			key = entry.getAttribute("key")
			if key == "finishTime":
				self.__finishTime = float(value)
			if key == "discardTime":
				self.__discardTime = float(value)

	def hasNext(self):
		return self.interpolatedEntries[0].hasNext()		

	def next(self):
		start = """<?xml version="1.0" encoding="UTF-8"?>\n""" + """<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">\n""" + """<properties>\n"""
		end = """</properties>"""

		configuration = start

		for staticEntry in self.staticEntries:
			configuration = configuration + staticEntry.toxml() + "\n"

		interpolatedEntry = self.interpolatedEntries[0]

		value = interpolatedEntry.next()
		
		self.__tag = str(value)
		self.__type = interpolatedEntry.getText()

		dynamicEntry = "<entry key=\"" + interpolatedEntry.getKey() + "\">" + str(value) + "</entry>"

		configuration = configuration + dynamicEntry + "\n"
		
		configuration = configuration + "<entry key=\"taxonomyFile\">taxonomy.xml</entry>\n"

		configuration = configuration + end + '\n'
		
		start = """<?xml version="1.0" encoding="UTF-8"?>\n""" + """<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">\n""" + """<experiment>\n"""
		end = """</experiment>"""

		generatedExpConfig = start
		
		generatedExpConfig += "<staticConfig>\n"

		for staticEntry in self.staticEntries:
			generatedExpConfig = generatedExpConfig + staticEntry.toxml() + "\n"

		dynamicEntry = "<entry key=\"" + interpolatedEntry.getKey() + "\">" + str(value) + "</entry>"

		generatedExpConfig = generatedExpConfig + dynamicEntry + "\n"
		
		generatedExpConfig += "</staticConfig>\n"
		
		generatedExpConfig += "<repeat number=\"%s\"/>\n" % self.getRepeat()
		
		generatedExpConfig += "<measures>\n"
		
		for measure in self.__measures:
			generatedExpConfig = generatedExpConfig + measure.toxml() + "\n"
		
		generatedExpConfig += "</measures>\n"

		generatedExpConfig = generatedExpConfig + end + '\n'

		return configuration, generatedExpConfig
	
	def getTag(self):
		return self.__tag
	
	def getType(self):
		return self.__type
	
	def getRepeat(self):
		return self.__repeat
	
	def getSimulationTime(self):
		return self.__finishTime
	
	def getDiscardTime(self):
		return self.__discardTime
	
def main():
	configGenerator = ConfigGenerator("ExpConfig.xml")

	while configGenerator.hasNext():
		config = configGenerator.next()
		print config

if __name__ == '__main__':
	 main()

