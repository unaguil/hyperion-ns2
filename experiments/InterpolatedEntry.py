import numpy

class InterpolatedEntry:
	def __init__(self, key, interpolator, text, start, end, step):
		self.key = key
		self.interpolator = interpolator
		self.start = start
		self.end = end
		self.step = step
		self.text = text

		if step == 0 or start == end:
			self.values = [start]
		else:
			self.values = numpy.arange(start, end + step, step) 

		self.current = 0
		
		self.__currentValue = None

	def next(self):
		self.__currentValue = self.values[self.current]
		self.current = self.current + 1
		return self.__currentValue

	def hasNext(self):
		return self.current < len(self.values)
		
	def currentValue(self):
		return self.__currentValue

	def getKey(self):
		return self.key
	
	def getText(self):
		return self.text

def main():
	ie = InterpolatedEntry("test.test", "interpolator", 0, 10, 1)
	
	print ie.getKey()

	while ie.hasNext():
		print ie.next()

if __name__ == '__main__':
    main()

