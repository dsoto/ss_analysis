'''
Total watthours distributed vs. time
X-axis is december 1 through 31, Y axis is total delivered watt-hours. 
This is the total watt-hours delivered (does not include meter/mains
consumption, only individual consumers)... basically shows the story of
how much use the system has gotten.

loop through all data and integrate watt hours
- incorporate integrate watt-hours as function in ss_plotting.py


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
    #dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    axis.xaxis.set_major_formatter(dateFormatter)
    axis.set_xlabel('Date')
    axis.set_ylabel('Power Consumption (Watt-hours)')
    axis.set_ylim((0, 1000))
    fig.autofmt_xdate()


dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'
plotCircuitList = ['201','202','203','204','205','206','207','208','209','210','211','212']
dateRangeStart = datetime.datetime(2010, 12, 17)
dateRangeEnd = datetime.datetime(2010, 12, 30)
totalPower = []

# loop through days 
# for each day compute total use and store in array
days = (dateRangeEnd - dateRangeStart).days
days = range(days)

dayRange = []
totalWattHours = []
scWattHours = []
for day in days:
    dateStart = dateRangeStart + datetime.timedelta(days=day)
    dateEnd = dateStart + datetime.timedelta(days=1)
    totalWattHoursForDay = 0
    for circuit in plotCircuitList:
        data = ssp.getFormattedData(circuit, dateStart, dateEnd, 1, dataDirectory)
        if data == []:
            #print 'no data for', dateStart, circuit
            integral = 0
            scwht = 0
        else:
            dts = map(dateutil.parser.parse,data['Time Stamp'])
            mpldays = matplotlib.dates.date2num(dts)
            integral = scipy.integrate.trapz(data['Watts'],dx=3.0/60/60)
            scwht = data['Watt Hours Today'][-1]

        totalWattHoursForDay += integral
        print dateStart.month, dateStart.day, circuit, integral
        print dateStart.month, dateStart.day, circuit, scwht

    print totalWattHoursForDay
    dayRange.append(dateStart)
    totalWattHours.append(totalWattHoursForDay)
    
mpldays = matplotlib.dates.date2num(dayRange)
fig, axis = getFigure()
axis.plot_date(dayRange, totalWattHours,'-')
formatFigure(fig, axis)
fig.savefig('3.pdf')