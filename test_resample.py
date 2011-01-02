# script to plot histogram of power consumption

import ss_plotting as ssp
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import datetime

def resampleData(data, dateStart, dateEnd, dt):
    # convert time string to seconds
    #time = map(int, data[:,0])
    #time = map(str, time)
    # parsedDates are datetime objects
    parsedDates = [dateutil.parser.parse(t) for t in data['Time Stamp']]
    # mplDates are days 
    mplDates = matplotlib.dates.date2num(parsedDates)
    
    
    oldSeconds = [(date - dateStart).days * 86400 + 
                  (date - dateStart).seconds for date in parsedDates]
    #print oldSeconds
        
    # loop through newSeconds and find new values
    # for power, if no neighboring value, power = 0
    # make newSeconds deal with dateStart and dateEnd
    totalSeconds = (dateEnd - dateStart).days * 86400 + (dateEnd - dateStart).seconds
    newSeconds = np.arange(0, totalSeconds+1, 60)

    newPower = np.zeros(len(newSeconds))
    
    for i, second in enumerate(newSeconds):
        # find nearest oldSeconds sample
        delta = min(abs(oldSeconds - second))
        index = np.argmin(abs(oldSeconds - second))
        if delta < 15:
            newPower[i] = data['Watts'][index]        

    return newSeconds, newPower

def getFigure():
    fig = plt.figure()
    axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
    return fig, axis

def formatFigure(fig, axis):
    dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
    axis.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()


plotDate = '12/27'
plotCircuit = '211'
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'
downsample = 1
plotCircuitList = ['200','201','202','203','205','206','207','208','209','210','211','212']
#plotCircuitList = ['200']
dateStart = datetime.datetime(2010, 12, 25)
dateEnd = datetime.datetime(2010, 12, 27)

#totalPower = np.zeros(len(newSeconds))
totalPower = []

for plotCircuit in plotCircuitList:
    data = ssp.getFormattedData(plotCircuit, dateStart, dateEnd, 1, dataDirectory)
    
    dt = 60
    newSeconds, newPower = resampleData(data, dateStart, dateEnd, dt)
    
    #convert newSeconds to datetime objects and then mpl days

    
    newTime = [(dateStart + datetime.timedelta(seconds=int(second))) 
                for second in newSeconds]
    newTime = matplotlib.dates.date2num(newTime)
    newTime = []
    for second in newSeconds:
        deltaDays = second / 86400
        deltaSeconds = second % 86400
        newTime.append(dateStart+ datetime.timedelta(days = int(deltaDays),
                                                     seconds = int(deltaSeconds)))
    newTime = matplotlib.dates.date2num(newTime)
                                                     
    # parsedDates are datetime objects
    parsedDates = [dateutil.parser.parse(t) for t in data['Time Stamp']]
    # mplDates are days 
    mplDates = matplotlib.dates.date2num(parsedDates)
    
    if '200' not in plotCircuit:
        if totalPower == []:
            totalPower = newPower
        else:
            totalPower += newPower
    
    fig, axis = getFigure()
    axis.plot_date(newTime,newPower,'-')
    #axis.plot_date(mplDates,data['Watts'],'+')
    formatFigure(fig, axis)    
    plotFileName = 'rs_' + plotCircuit + '.pdf'
    print 'writing', plotFileName
    fig.savefig(plotFileName)

fig, axis = getFigure()
axis.plot_date(newTime,totalPower,'-')
formatFigure(fig, axis)
plotFileName = 'rs_total.pdf'
fig.savefig(plotFileName)

