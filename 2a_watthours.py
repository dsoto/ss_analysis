'''
X axis is midnight to midnight (or 6am to 6am), Y-axis is watthours...
plots is of "typical" watthours (not sure if you just lay-over all
consumers, each day & take an average?)  What is the typical usage look
like?

For a watt-hour vs. time of day plot - maybe instead of my earlier idea
of combining/averaging everything into one plot (not sure how you'd do
this) would it be easiest to just pick 1 "representative" day, and
pretty much use the format you have (where you show all 12 circuits, but
no mains)... maybe a recent day this week when the service was up all
day, and when consumers were using based on the understanding that their
use was "allocated" and they were going to have to start paying for
it... as apposed to earlier in the month when they were leaving lights
on all the time... what do you think?

choose day
resample data
show all consumers and total

'''

import ss_plotting as ssp
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import datetime


def getFigure():
    fig = plt.figure()
    axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
    return fig, axis

def formatFigure(fig, axis):
    dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
    axis.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()
    axis.grid()
    axis.set_title('Consumption for '+str(dateStart.month)+'-'+str(dateStart.day))
    axis.set_xlabel('Time of Day')
    axis.set_ylabel('Energy Consumption (Watt-Hours)')
    axis.legend(loc=(1.0,0.0), title='Circuit', numpoints=1)


dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'
plotCircuitList = ['201','202','203','205','206','207','208','209','210','211','212']
#plotCircuitList = ['201']
dateStart = datetime.datetime(2010, 12, 27)
dateEnd = datetime.datetime(2010, 12, 28)
plotColorList  = ['b', 'r', 'g', 'k', 'b', 'r', 'g', 'k', 'b', 'r', 'g', 'k']
plotSymbolList  = ['x', 'x', 'x', 'x', 's', 's', 's', 's', 'd', 'd', 'd', 'd']


totalPower = []
fig, axis = getFigure()

for i, plotCircuit in enumerate(plotCircuitList):
    print 'getting data for circuit ' + plotCircuit
    data = ssp.getFormattedData(plotCircuit, dateStart, dateEnd, 1, dataDirectory)
    
    dt = 10*60
    print 'resampling data for ' + plotCircuit
    newSeconds, newData = ssp.resampleData(data, 'Watt Hours Today', dateStart, dateEnd, dt)
    
    #convert newSeconds to datetime objects and then mpl days

    print 'parsing dates for plotting'
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
    

    print 'plotting'
    if data != []:
        axis.plot_date(newTime, newData,
                       ls = '-',
                       color = plotColorList[i],
                       marker = plotSymbolList[i], 
                       markeredgecolor = plotColorList[i], 
                       markerfacecolor = 'None',
                       label=plotCircuit)

formatFigure(fig, axis)    
fig.savefig('2a.pdf')
