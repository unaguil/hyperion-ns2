
def getTimeRange(timeRange, finishTime):
        init, end = timeRange
        
        if init == 'START':
            init = 0.0
            
        if end == 'END' or end >= finishTime:
            end = finishTime
            
        return (init, end)