'''
averages power consumption information over multiple days
'''

import ss_plotting as ssp
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import datetime
import scipy.integrate

def getFigure():
    fig = plt.figure()
    axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
    return fig, axis

def formatFigure(fig, axis):
    dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
    #dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    axis.xaxis.set_major_formatter(dateFormatter)
    axis.set_xlabel('Date')
    axis.set_ylabel('Power Consumption (Watt-hours)')
    #axis.set_ylim((0, 1000))
    fig.autofmt_xdate()


dataDirectory = 'data/'
plotCircuitList = ['200','201','202','203','205','206','207','208','209','210','211','212']
circuit = '207'
dateRangeStart = datetime.datetime(2011, 01, 01)
dateRangeEnd = datetime.datetime(2011, 02, 1)

# loop through days
# for each day compute total use and store in array
days = (dateRangeEnd - dateRangeStart).days
days = range(days)

for circuit in plotCircuitList:
    print 'getting data for circuit', circuit
    data = []
    for day in days:
        dateStart = dateRangeStart + datetime.timedelta(days=day)
        dateEnd = dateStart + datetime.timedelta(days=1)

        tempData = ssp.getFormattedData(circuit, dateStart, dateEnd, 1, dataDirectory)

        if tempData != []:
            newTime, newData = ssp.resampleData(tempData, 'Watts', dateStart, dateEnd, 10*60)
        else:
            print 'no data for', dateStart, circuit

        if newData == []:
            print 'no data for', dateStart, circuit
        else:
            if data == []:
                data = newData
            else:
                data += newData
        data /= (dateRangeEnd - dateRangeStart).days
    # what is time axis now that there are different days being consolidated?
    mpldays = matplotlib.dates.date2num(newTime)
    fig, axis = getFigure()
    print 'plotting circuit', circuit
    axis.plot_date(mpldays, data,'-')
    formatFigure(fig, axis)
    fig.savefig('averaged_'+circuit+'.pdf')