# script to plot histogram of power consumption

import ss_plotting as ssp
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import datetime

plotDate = '12/27'
plotCircuit = '211'
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/2010'
downsample = 1
plotCircuitList = ['201','202','203','205','206','207','208','209','210','211','212']

dateStart = datetime.datetime(2010, 12, 26)

def resampleData(data, dt):
    # convert time string to seconds
    time = map(int, data[:,0])
    time = map(str, time)
    # parsedDates are datetime objects
    parsedDates = [dateutil.parser.parse(t) for t in time]
    # mplDates are days 
    mplDates = matplotlib.dates.date2num(parsedDates)
    
    
    oldSeconds = [(date - dateStart).seconds for date in parsedDates]
    #print oldSeconds
        
    # loop through newSeconds and find new values
    # for power, if no neighboring value, power = 0
    
    newPower = np.zeros(len(newSeconds))
    
    for i, second in enumerate(newSeconds):
        # find nearest oldSeconds sample
        delta = min(abs(oldSeconds - second))
        index = np.argmin(abs(oldSeconds - second))
        if delta < 15:
            newPower[i] = data[index, 1]        

    return newSeconds, newPower

newSeconds = np.arange(0, 86400+1, 60)

totalPower = np.zeros(len(newSeconds))

for plotCircuit in plotCircuitList:

    data = ssp.getData(plotCircuit, plotDate, downsample, dataDirectory)
    
    newSeconds, newPower = resampleData(data, 60)
    
    #convert newSeconds to datetime objects and then mpl days
    
    newTime = [(dateStart + datetime.timedelta(days=1,seconds=int(second))) 
                for second in newSeconds]
    newTime = matplotlib.dates.date2num(newTime)
    
    time = map(int, data[:,0])
    time = map(str, time)
    # parsedDates are datetime objects
    parsedDates = [dateutil.parser.parse(t) for t in time]
    # mplDates are days 
    mplDates = matplotlib.dates.date2num(parsedDates)
    
    totalPower += newPower
    
    fig = plt.figure()
    axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
    axis.plot_date(newTime,newPower,'x-')
    axis.plot_date(mplDates,data[:,1],'+')
    plotFileName = 'rs_' + plotCircuit + '.pdf'
    print 'writing', plotFileName
    fig.savefig(plotFileName)

fig = plt.figure()
axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
axis.plot_date(newTime,totalPower,'x-')
plotFileName = 'rs_total.pdf'
fig.savefig(plotFileName)


