from LinearInterpolator import LinearInterpolator

class IntegerInterpolator(LinearInterpolator):
    def __init__(self, entry):
        LinearInterpolator.__init__(self, entry)
        
    def next(self):
        return int(LinearInterpolator.next(self))
        
    def currentValue(self):
        return int(LinearInterpolator.currentValue(self)) 