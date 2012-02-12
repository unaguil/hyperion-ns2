
MESSAGES = 'messages'
RATIO = '[0.0 - 0.1] ratio'
NEIGHBORS = 'neighbors'
PARAMETERS = 'parameters'
MILLIS = 'milliseconds'
SECONDS = 'seconds'
COMPOSITIONS = 'compositions'
SEARCHES = 'searches'
HOPS = 'hops'
MESSAGE_OVERHEAD = 'messages/s node'
MESSAGE_TRAFFIC_OVERHEAD = 'KB/s node'

def str_formatter(units, value):
    if units == MILLIS:
        return '%.0f' % value
    if units == SECONDS:
        return '%.3f' % value
    
    return '%.2f' % value