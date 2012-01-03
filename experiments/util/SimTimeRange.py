
def getTimeRange(timeRange, finishTime, discardTime):
        init, duration = timeRange
        
        if init == 'START':
            init = discardTime
            
        end = init + duration
            
        if end >= finishTime:
            end = finishTime
            
        return (init, end)