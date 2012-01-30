from interpolators.LinearInterpolator import LinearInterpolator
from interpolators.IntegerInterpolator import IntegerInterpolator
from interpolators.SetInterpolator import SetInterpolator

def loadInterpolator(entry):
    interpolator = entry.getAttribute("interpolator")
    
    if interpolator == 'LinearInterpolator':
        return LinearInterpolator(entry)
    if interpolator == 'IntegerInterpolator':
        return IntegerInterpolator(entry)
    if interpolator == 'SetInterpolator':
        return SetInterpolator(entry)
    
    raise Exception('Unknown interpolator %s' % interpolator)