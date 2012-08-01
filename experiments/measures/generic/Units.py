
MESSAGES = 'mensajes'
RATIO = '%'
NEIGHBORS = 'vecinos'
PARAMETERS = 'parameters'
MILLIS = 'ms'
SECONDS = 's'
COMPOSITIONS = 'compositions'
SEARCHES = 'searches'
HOPS = 'hops'
MESSAGE_OVERHEAD = 'messages/s node'
MESSAGE_TRAFFIC_OVERHEAD = 'KB/s'

def str_formatter(units, value):
    if units == MILLIS:
        return '%.0f' % value
    if units == SECONDS:
        return '%.3f' % value
    if units == RATIO:
        return '%.2f' % (value * 100.0)
    
    return '%.2f' % value