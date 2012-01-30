import numpy

class SetInterpolator:
	def __init__(self, dynamicEntry):
		self.__key = dynamicEntry.getAttribute("key")
		self.__values = eval(dynamicEntry.getAttribute("values"))
		self.__text = dynamicEntry.getAttribute("text")

		self.__index = 0
		self.__currentValue = None

	def next(self):
		self.__currentValue = self.__values[self.__index]
		self.__index += 1
		return self.__currentValue

	def hasNext(self):
		return self.__index < len(self.__values)
		
	def currentValue(self):
		return self.__currentValue

	def getKey(self):
		return self.__key
	
	def getText(self):
		return self.__text
	