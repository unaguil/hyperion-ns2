
def getTimeRange(timeRange, finishTime, discardTime):
        init, end = timeRange
        
        if init == 'START':
            init = discardTime
            
        if end == 'END' or end >= finishTime:
            end = finishTime
            
        return (init, end)