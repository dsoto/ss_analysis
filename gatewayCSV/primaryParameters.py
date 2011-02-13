# plot primary parameter logs

import numpy as np
import dateutil.parser
import matplotlib.dates
import matplotlib.pyplot as plt
import datetime


dataFileName = 'primaryParameters.csv'
usecols = [0,5,6,7,8,9]
plotColorList  = ['b', 'r', 'g', 'k', 'b', 'r', 'g', 'k', 'b', 'r', 'g', 'k']
plotSymbolList  = ['x', 'x', 'x', 'x', 's', 's', 's', 's', 'd', 'd', 'd', 'd']
dateStart = datetime.datetime(2011, 2, 04)
dateEnd = datetime.datetime(2011, 2, 15)

def creditScrub(val):
    if val=='None':
        return 0.0
    else:
        val = float(val)
        if val < 0:
            val = 0
        return val
        
def getDataAsRecordArray(dateStart, dateEnd):
    dtype = [('watthours',   'float'),
             ('circuit_id',  'int'),
             ('use_time',    'float'),
             ('credit',      'float'),
             ('circuit',     'S30'),
             ('date',        'object')]
    dtype = np.dtype(dtype)

    # load file
    d = np.loadtxt(dataFileName, delimiter=',', 
                                 skiprows=1,
                                 dtype = dtype,
                                 converters = {7: creditScrub,
                                               9: dateutil.parser.parse},
                                 usecols=usecols)

    # yank irrelevant circuits
    d = d[d['circuit_id']!=25]
    d = d[d['circuit_id']!=28]
    d = d[d['circuit_id']!=29]
    d = d[d['circuit_id']!=30]
    
    # take out relevant date range
    d = d[(d['date'] > dateStart) & (d['date'] < dateEnd)]
    
    # sort by date
    sortIndex = d['date'].argsort()
    d = np.take(d, sortIndex)
    
    return d
    
def getDataAsDict(dataFileName, usecols, dateStart, dateEnd):
    d = np.loadtxt(dataFileName, delimiter=',', 
                                 dtype=str, 
                                 skiprows=1,
                                 usecols=usecols)
    
    # scrub data and remove 'None'
    for i,a in enumerate(d[:,3]):
        if a == 'None':
            d[i,3] = 0
    
    # find the set of circuits from data and remove mains
    circuits = set(d[:,1])
    circuits.remove('25')        # remove mains
    circuits.remove('28')        # remove independent
    circuits.remove('29')        # remove independent
    circuits.remove('30')        # remove independent

    # mask off for desired date range
    dates = map(dateutil.parser.parse, d[:,5])
    dates = np.array(dates)
    dateMask = (dates > dateStart) & (dates < dateEnd)
    d = d[dateMask]

    # create dictionary of lists
    dataDict = {}
    for c in circuits:
        dataDict[c] = []
        for a in d:
            if a[1]==c:
                dataDict[c].append(a)
                
    # convert to proper np.arrays
    for c in circuits:
        dataDict[c] = np.array(dataDict[c])
    
    circuitMask = (d[:,1]!='25') & (d[:,1]!='28') & (d[:,1]!='29') & (d[:,1]!='30')
    d = d[circuitMask]
    
    return d, dataDict

def plotCredit(dataDict):
    recharge = []
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    circuits = dataDict.keys()
    for i,c in enumerate(circuits):
        textDates = dataDict[c][:,5]
        dates = map(dateutil.parser.parse, textDates)
        dates = matplotlib.dates.date2num(dates)
        credit = map(float, dataDict[c][:,3])
        wh = map(float, dataDict[c][:,0])
        
        sortIndices = dates.argsort()
        credit = np.take(credit, sortIndices)
        wh = np.take(wh, sortIndices)
        dates.sort()
        
        
        # pull out recharge events
        cd = np.diff(credit)
        cmask = cd > 0
        for element in zip(textDates[cmask],cd[cmask]):
            recharge.append(element)
        
        # plot masked data to get date range
        ax.plot_date(dates, credit, '-o', label=c,
                                   color = plotColorList[i],
                                   marker = plotSymbolList[i],
                                   markeredgecolor = plotColorList[i],
                                   markerfacecolor = 'None')
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)
        fig.autofmt_xdate()
    
        #plt.plot_date(dates, wh, '-o', label=c)
        ax.legend(loc=(1.0,0.0))
        #plt.show()
        ax.grid()
        
        fig.savefig('credit.pdf')
        #plt.close()
    return recharge

def plotRecharges(dataDict):
    recharge = []
    
    circuits = dataDict.keys()
    for i,c in enumerate(circuits):
        textDates = dataDict[c][:,5]
        dates = map(dateutil.parser.parse, textDates)
        dates = matplotlib.dates.date2num(dates)
        credit = map(float, dataDict[c][:,3])
        
        sortIndices = dates.argsort()
        credit = np.take(credit, sortIndices)
        dates.sort()
        
        # pull out recharge events
        cd = np.diff(credit)
        cmask = cd > 0
        for element in zip(textDates[cmask],cd[cmask]):
            recharge.append(element)    

    recharge = np.array(recharge)
    
    rechargeFCFA = map(float, recharge[:,1])
    rechargeDate = map(dateutil.parser.parse, recharge[:,0])
    rechargeDate = matplotlib.dates.date2num(rechargeDate)
    
    sortIndices = rechargeDate.argsort()
    rechargeFCFA = np.take(rechargeFCFA, sortIndices)
    rechargeDate.sort()
    
    for element in zip(rechargeDate, rechargeFCFA):
        print element
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    plt.plot_date(rechargeDate, rechargeFCFA)
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()
    
    ax.grid()
    fig.savefig('recharges.pdf')

def plotWattHoursOld(dataDict):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    circuits = dataDict.keys()
    for i,c in enumerate(circuits):
        # get last watt hour reading for each day and store in array
        # make datetime objects
        # mask = dates < dateEnd
        # pull last value in array
        
        textDates = dataDict[c][:,5]
        dates = map(dateutil.parser.parse, textDates)
        dates = matplotlib.dates.date2num(dates)
        wh = map(float, dataDict[c][:,0])
        
        sortIndices = dates.argsort()
        wh = np.take(wh, sortIndices)
        dates.sort()
                
        # plot masked data to get date range
        ax.plot_date(dates, wh, '-o', label=c,
                                   color = plotColorList[i],
                                   marker = plotSymbolList[i],
                                   markeredgecolor = plotColorList[i],
                                   markerfacecolor = 'None')
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)
        fig.autofmt_xdate()
    
        #plt.plot_date(dates, wh, '-o', label=c)
        ax.legend(loc=(1.0,0.0))
        #plt.show()
        ax.grid()
        
        fig.savefig('watthoursold.pdf')

def plotWattHoursPerDayOld(dataDict, dateStart, dateEnd):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    circuits = dataDict.keys()
    consumption = {}
    
    # loop through dates
    for i,c in enumerate(circuits):
        consumption[c] = []
        # get last watt hour reading for each day and store in array
        # make datetime objects
        # mask = dates < dateEnd
        # pull last value in array

        textDates = dataDict[c][:,5]
        dates = map(dateutil.parser.parse, textDates)
        dates = np.array(dates)
        wh = map(float, dataDict[c][:,0])
        wh = np.array(wh)
        sortIndices = dates.argsort()
        wh = np.take(wh, sortIndices)
        dates.sort()

        dateCurrent = dateStart
        while dateCurrent <= dateEnd:
            dateLast = dateCurrent
            dateCurrent = dateCurrent + datetime.timedelta(days=1)
            mask = (dates > dateLast) & (dates < dateCurrent)
            print dateCurrent
            print 'increment'
            if dates[mask].shape != (0,):
                print dates[mask][-1]        
                consumption[c] += wh[mask][-1]
            else:
                pass
                # this value of watt hours = 0

def plotWattHours(d):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    circuits = set(d['circuit_id'])
    
    for i,c in enumerate(circuits):
        mask = d['circuit_id']==c
        dates = d[mask]['date']
        dates = matplotlib.dates.date2num(dates)
        wh = d[mask]['watthours']
        
        # plot masked data to get date range
        ax.plot_date(dates, wh, '-o', label=str(c),
                                   color = plotColorList[i],
                                   marker = plotSymbolList[i],
                                   markeredgecolor = plotColorList[i],
                                   markerfacecolor = 'None')
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)
        fig.autofmt_xdate()
    
        #plt.plot_date(dates, wh, '-o', label=c)
        ax.legend(loc=(1.0,0.0))
        #plt.show()
        ax.grid()
        
        fig.savefig('plotWattHours.pdf')

def plotAllWattHours(d):
    '''
    for each date in d, sum watt hours and report
    '''
    
    dates = set(d['date'])
    
    plotDates = np.array([])
    plotWattHours = np.array([])

    for date in dates:
        sum = d[d['date']==date]['watthours'].sum()
        print date, sum
        plotDates = np.append(plotDates, date)
        plotWattHours = np.append(plotWattHours, sum)

    plotDates = matplotlib.dates.date2num(plotDates)

    sortIndices = plotDates.argsort()
    wh = np.take(plotWattHours, sortIndices)
    plotDates.sort()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    plt.plot_date(plotDates, wh, '-')
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()
    
    ax.grid()
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (Watt-Hours)')
    ax.set_title('Cumulative Energy Consumed (Reset Daily)')
    fig.savefig('plotAllWattHours.pdf')

def plotTotalWattHoursPerDay(d):
    mask = []
    for date in d['date']:
        if date.hour==23:
            mask.append(True)
        else:
            mask.append(False)
    
    mask = np.array(mask)
    d = d[mask]

    dates = set(d['date'])
    
    plotDates = np.array([])
    plotWattHours = np.array([])

    for date in dates:
        sum = d[d['date']==date]['watthours'].sum()
        print date, sum
        plotDates = np.append(plotDates, date)
        plotWattHours = np.append(plotWattHours, sum)

    sortIndices = plotDates.argsort()
    plotWattHours = np.take(plotWattHours, sortIndices)
    plotDates.sort()

    plotDates = matplotlib.dates.date2num(plotDates)


    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    plt.plot_date(plotDates, plotWattHours, '-')
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()
    
    ax.grid()
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (Watt-Hours)')
    ax.set_ylim(bottom=0)
    ax.set_title('Cumulative Energy Consumed (Reset Daily)')
   
    fig.savefig('plotHouseholdWattHoursPerDay.pdf')

def plotHouseholdWattHoursPerDay(d, dateStart, dateEnd):
    # loop through dates from dateStart to dateEnd
    # find date closest to midnight
    # create list by circuit and plot

    mask = []
    for date in d['date']:
        if date.hour==23:
            mask.append(True)
        else:
            mask.append(False)
    
    mask = np.array(mask)
    d = d[mask]

    circuits = set(d['circuit_id'])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for i,c in enumerate(circuits):
        mask = d['circuit_id']==c
        dates = d[mask]['date']
        dates = matplotlib.dates.date2num(dates)
        wh = d[mask]['watthours']
        
        # plot masked data to get date range
        ax.plot_date(dates, wh, '-o', label=str(c),
                                   color = plotColorList[i],
                                   marker = plotSymbolList[i],
                                   markeredgecolor = plotColorList[i],
                                   markerfacecolor = 'None')
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)
        fig.autofmt_xdate()
    
        #plt.plot_date(dates, wh, '-o', label=c)
        ax.legend(loc=(1.0,0.0))
        #plt.show()
        ax.grid()
        
        fig.savefig('plotHouseholdWattHoursPerDay.pdf')


d = getDataAsRecordArray(dateStart, dateEnd)
plotAllWattHours(d)
plotWattHours(d)
plotTotalWattHoursPerDay(d)

'''
d, dataDict = getDataAsDict(dataFileName, usecols, dateStart, dateEnd)
plotAllWattHours(d)
plotWattHoursPerDay(dataDict, dateStart, dateEnd)
plotCredit(dataDict)
plotWattHours(dataDict)
plotRecharges(dataDict)
'''