from interpolators.LinearInterpolator import LinearInterpolator
from interpolators.IntegerInterpolator import IntegerInterpolator

def loadInterpolator(entry):
    interpolator = entry.getAttribute("interpolator")
    
    if interpolator == 'LinearInterpolator':
        return LinearInterpolator(entry)
    if interpolator == 'IntegerInterpolator':
        return IntegerInterpolator(entry)
    
    raise Exception('Unknown interpolator %s' % interpolator)