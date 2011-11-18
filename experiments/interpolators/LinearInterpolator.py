import numpy

class LinearInterpolator:
	def __init__(self, dynamicEntry):
		self.__key = dynamicEntry.getAttribute("key")
		self.__start = float(dynamicEntry.getAttribute("start"))
		self.__end = float(dynamicEntry.getAttribute("end"))
		self.__step = float(dynamicEntry.getAttribute("step"))
		self.__text = dynamicEntry.getAttribute("text")

		if self.__step == 0 or self.__start == self.__end:
			self.__values = [self.__start]
		else:
			self.__values = numpy.arange(self.__start, self.__end + self.__step, self.__step) 

		self.__current = 0
		
		self.__currentValue = None

	def next(self):
		self.__currentValue = self.__values[self.__current]
		self.__current += 1
		return self.__currentValue

	def hasNext(self):
		return self.__current < len(self.__values)
		
	def currentValue(self):
		return self.__currentValue

	def getKey(self):
		return self.__key
	
	def getText(self):
		return self.__text
	