# plot primary parameter logs

import numpy as np
import dateutil.parser
import matplotlib.dates
import matplotlib.pyplot as plt
import datetime
import os.path


usecols = [0,5,6,7,8,9]
plotColorList  = ['b', 'r', 'g', 'k', 'b', 'r', 'g', 'k', 'b', 'r', 'g', 'k']
plotSymbolList  = ['x', 'x', 'x', 'x', 's', 's', 's', 's', 'd', 'd', 'd', 'd']
dateStart = datetime.datetime(2011,  1,  1)
dateEnd   = datetime.datetime(2011,  2,  28)

def creditScrub(val):
    ''' take out values of None from the data on import '''
    if val=='None':
        return 0.0
    else:
        val = float(val)
        if val < 0:
            val = 0
        return val

def getDataAsRecordArray(dateStart, dateEnd):
    '''
    load csv from shared solar gateway and create
    numpy record array
    also, remove MAINS and independence circuits
    only return data for date range between dateStart and dateEnd
    '''
    dtype = [('watthours',   'float'),      # column 0
             ('circuit_id',  'int'),        # column 5
             ('use_time',    'float'),      # column 6
             ('credit',      'float'),      # column 7
             ('circuit',     'S30'),        # column 8
             ('date',        'object')]     # column 9
    dtype = np.dtype(dtype)

    # either get file from web or use existing file on computer
    fileName = 'dataFile.csv'
    if os.path.isfile(fileName):
        # file exists so loadtxt uses csv file
        print 'loading', fileName
        print 'new data is _NOT_ being downloaded'
        print 'remove dataFile.csv to download fresh data'
        dataStream = open(fileName, 'r')
    else:
        # file does not exist so we must download it
        print 'opening url'
        import urllib
        dataString = urllib.urlopen('http://178.79.140.99/sys/export?model=PrimaryLog').read()

        print 'converting to cStringIO'
        import cStringIO
        dataStream = cStringIO.StringIO(dataString)

        # dump csv data to file
        f = open('dataFile.csv','w')
        f.write(dataString)
        f.close()

    print 'np.loadtxt'
    # load file
    d = np.loadtxt(dataStream, delimiter=',',
                               skiprows=1,
                               dtype = dtype,
                               converters = {7: creditScrub,
                                             9: dateutil.parser.parse},
                               usecols=usecols)

    # yank irrelevant circuits
    d = d[d['circuit_id']!=25]     #MAINS pelengana
    d = d[d['circuit_id']!=28]
    d = d[d['circuit_id']!=29]
    d = d[d['circuit_id']!=30]

    # take out relevant date range
    #d = d[(d['date'] > dateStart) & (d['date'] < dateEnd)]

    # sort by date
    sortIndex = d['date'].argsort()
    d = np.take(d, sortIndex)

    return d

def plotCreditSeparateAxes(d):
    '''
    plots the credit in each circuit account on a separate axis
    '''
    fig = plt.figure(figsize=(8,12))
    circuits = set(d['circuit_id'])

    for i,c in enumerate(circuits):
        # assemble data by circuit
        circuitMask = d['circuit_id'] == c
        dates = matplotlib.dates.date2num(d[circuitMask]['date'])
        credit = d[circuitMask]['credit']

        # plot individual circuit data
        if i == 0:
            ax = fig.add_axes((0.15,0.1+i*0.072,0.7,0.05))
        else:
            ax = fig.add_axes((0.15,0.1+i*0.072,0.7,0.05))
        ax.plot_date(dates, credit, '-x')
        ax.text(1.05, 0.4, c, transform = ax.transAxes)
        ax.set_yticks((0,500,1000))
        oldax = ax
        ax.set_ylim((0,1000))
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)
        if i==0:
            ax.set_xlabel('Date')
        if i!=0:
            ax.set_xticklabels([])

    fig.text(0.05, 0.7, 'Account Credit (FCFA)', rotation='vertical')
    fig.suptitle('Account Credit in Pelengana')
    fig.savefig('plotCreditSeparateAxes.pdf')

def plotRecharges(d):
    '''
    plots recharge events and outputs statistics on recharges
    '''
    recharge = []
    rechargedCircuits = []

    circuits = set(d['circuit_id'])
    print 'all circuits', circuits
    for i,c in enumerate(circuits):
        circuitMask = d['circuit_id'] == c
        dates = d[circuitMask]['date']
        credit = d[circuitMask]['credit']

        # pull out recharge events
        cd = np.diff(credit)
        cmask = cd > 0
        for element in zip(dates[cmask],cd[cmask]):
            rechargedCircuits.append(c)
            recharge.append(element)

    print 'circuits that have recharged', set(rechargedCircuits)

    recharge = np.array(recharge)

    rechargeFCFA = recharge[:,1]
    rechargeDate = recharge[:,0]

    masklow = (rechargeFCFA > 400)
    rechargeFCFA = rechargeFCFA[masklow]
    rechargeDate = rechargeDate[masklow]

    mask500 = (rechargeFCFA > 400) & (rechargeFCFA < 600)
    rechargeFCFA[mask500] = 500
    print 'number of 500 recharges =', len(rechargeFCFA[mask500])

    mask1000 = (rechargeFCFA > 800) & (rechargeFCFA < 1200)
    rechargeFCFA[mask1000] = 1000
    print 'number of 1000 recharges =', len(rechargeFCFA[mask1000])

    print 'number of recharges',
    print len(rechargeFCFA)

    sortIndex = rechargeDate.argsort()
    rechargeFCFA = np.take(rechargeFCFA, sortIndex)
    rechargeDate = np.take(rechargeDate, sortIndex)

    for pair in zip(rechargeDate, rechargeFCFA):
        print pair[0].strftime('%m/%d %H:%M'),
        print str(pair[1]).rjust(10),
        print 'FCFA'

    avgHour = 0
    for date in rechargeDate:
        avgHour += date.hour / float(len(rechargeDate))

    print 'average time of recharge', avgHour

    rechargeDate = matplotlib.dates.date2num(rechargeDate)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.plot_date(rechargeDate, rechargeFCFA,
                  marker = 'o',
                  markeredgecolor = 'k',
                  markerfacecolor = 'None')
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount of Purchase (FCFA)')
    ax.set_title('Credit Purchases in Pelengana')
    ax.set_ylim((0,1050))
    ax.grid()
    fig.savefig('plotRecharges.pdf')

def plotHouseholdEnergyPerHour(d):
    '''
    plots a time series of accumulated watt hours
    for each circuit
    '''
    fig = plt.figure(figsize=(8,12))
    #ax = fig.add_axes((0.15,0.2,0.7,0.7))

    circuits = set(d['circuit_id'])

    for i,c in enumerate(circuits):
        mask = d['circuit_id']==c
        dates = d[mask]['date']
        dates = matplotlib.dates.date2num(dates)
        wh = d[mask]['watthours']

        ax = fig.add_axes((0.15,0.1+i*0.072,0.7,0.05))


        # plot masked data to get date range
        ax.plot_date(dates, wh, '-x')
        if i==0:
            ax.set_xlabel('Date')
        if i!=0:
            ax.set_xticklabels([])

        ax.text(1.05, 0.4, c, transform = ax.transAxes)
        ax.set_ylim((0,150))
        ax.set_yticks((0,50,100,150))
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)

    #fig.autofmt_xdate()
    fig.text(0.05,0.7, 'Energy Consumption (Watt-Hours)', rotation='vertical')
    fig.suptitle('Hourly Accumulated Consumption Per Household')
    fig.savefig('plotHouseholdEnergyPerHour.pdf')

def plotColloquium(d):
    '''
    plots a time series of accumulated watt hours
    for each circuit
    '''
    fig = plt.figure()
    #ax = fig.add_axes((0.15,0.2,0.7,0.7))

    circuits = set(d['circuit_id'])
    circuits = [17,23]
    for i,c in enumerate(circuits):
        mask = d['circuit_id']==c
        dates = d[mask]['date']
        dates = matplotlib.dates.date2num(dates)
        wh = d[mask]['watthours']

        plotHeight = 0.7 / len(circuits)
        ax = fig.add_axes((0.15, 0.1+i*(plotHeight+0.05), 0.7, plotHeight))


        # plot masked data to get date range
        ax.plot_date(dates, wh, '-x')
        if i==0:
            ax.set_xlabel('Date')
        if i!=0:
            ax.set_xticklabels([])

        ax.text(1.05, 0.4, c, transform = ax.transAxes)
        ax.set_ylim((0,150))
        ax.set_yticks((0,50,100,150))
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)

    #fig.autofmt_xdate()
    fig.text(0.05,0.7, 'Energy Consumption (Watt-Hours)', rotation='vertical')
    fig.suptitle('Hourly Accumulated Consumption Per Household')
    fig.savefig('plotColloquium.pdf')

def plotHouseholdEnergyPerDay(d):
    '''
    plan:

    change to stacked plot
    place watt-hour data in numpy array

    '''
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
    ax = fig.add_axes((0.15,0.2,0.7,0.7))


    for i,c in enumerate(circuits):
        mask = d['circuit_id']==c
        dates = d[mask]['date']
        print dates
        print 'date length', len(dates)
        dates = matplotlib.dates.date2num(dates)
        wh = d[mask]['watthours']
        print 'wh length', len(wh)

        # plot masked data to get date range
        ax.plot_date(dates, wh, '-o', label=str(c),
                                   color = plotColorList[i],
                                   marker = plotSymbolList[i],
                                   markeredgecolor = plotColorList[i],
                                   markerfacecolor = 'None')

    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()
    ax.legend(loc=(1.0,0.0))
    ax.grid(True)
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy Consumed (Watt-Hours)')
    ax.set_title('Daily Consumption Per Household')
    fig.savefig('plotHouseholdEnergyPerDay.pdf')

def plotAllWattHours(d):
    '''
    for each date in d, sum watt hours and report
    '''

    dates = set(d['date'])

    plotDates = np.array([])
    plotWattHours = np.array([])

    for date in dates:
        sum = d[d['date']==date]['watthours'].sum()
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

def plotTotalEnergyPerDay(d):
    '''
    plot energy consumed by all circuits for each day
    not including mains
    '''
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
        plotDates = np.append(plotDates, date)
        plotWattHours = np.append(plotWattHours, sum)

    sortIndices = plotDates.argsort()
    plotWattHours = np.take(plotWattHours, sortIndices)
    plotDates.sort()

    plotDates = matplotlib.dates.date2num(plotDates)


    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.plot_date(plotDates, plotWattHours, 'ok')
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()

    ax.grid()
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (Watt-Hours)')
    ax.set_ylim(bottom=0)
    ax.set_title('Total Household Energy Consumed Per Day')

    fig.savefig('plotTotalWattHoursPerDay.pdf')

def printDataCompleteness(d):
    dates = list(set(d['date']))
    dates.sort()
    for date in dates:
        dataPoints = d[d['date']==date]
        if len(dataPoints) != 0:
            print date, '-', str(len(dataPoints)).rjust(2), '-',
            circuits = dataPoints['circuit_id']
            circuits.sort()
            for i in range(13,26):
                if i in circuits:
                    print i,
                else:
                    print '  ',
            print

def plotAveragedHourlyEnergy(energy, dateStart, dateEnd):
    numCircuits = energy.shape[0]
    numDays     = energy.shape[1]
    numHours    = energy.shape[2]

    fig = plt.figure(figsize=(8,12))

    for i,c in enumerate(range(numCircuits)):
        ax = fig.add_axes((0.15,0.05+i*0.072,0.7,0.05))

        henergy = np.diff(energy[c], axis=1)
        henergy = np.hstack((energy[c, :, 0].reshape(numDays,1),henergy))

        for day in range(numDays):
            ax.plot(henergy[day],color='#dddddd')

        ax.plot(sum(henergy,0)/numDays,'k')
        ax.set_ylim((-5,50))
        ax.set_yticks((0,25,50))
        ax.set_xlim((0,23))
        ax.set_xticks((0,4,8,12,16,20,23))
        ax.text(1.05, 0.4, str(c+13), transform = ax.transAxes)
        ax.grid(True)
    fig.text(0.05, 0.7, 'Power Usage (W)', rotation='vertical')
    fig.suptitle('averaged power usage\n'+str(dateStart)+'\n'+str(dateEnd))
    fig.savefig('plotAveragedHourlyEnergy.pdf')

def plotAveragedAccumulatedHourlyEnergy(energy, dateStart, dateEnd):
    numCircuits = energy.shape[0]
    numDays     = energy.shape[1]
    numHours    = energy.shape[2]

    fig = plt.figure(figsize=(8,12))

    for i,c in enumerate(range(numCircuits)):
        ax = fig.add_axes((0.15,0.05+i*0.072,0.7,0.05))

        for day in range(numDays):
            ax.plot(energy[c, day, :],color='#dddddd')

        ax.plot(sum(energy[c],0)/numDays,'k')
        ax.set_ylim((0,150))
        ax.set_yticks((0,50,100,150))
        ax.set_xlim((0,23))
        ax.set_xticks((0,4,8,12,16,20,23))
        ax.text(1.05, 0.4, str(c+13), transform = ax.transAxes)
        ax.grid(True)
    fig.text(0.05, 0.7, 'Accumulated Energy Use (Wh)', rotation='vertical')
    fig.suptitle('averaged accumulated usage\n'+str(dateStart)+'\n'+str(dateEnd))
    fig.savefig('plotAveragedAccumulatedHourlyEnergy.pdf')

def sampleHourlyWatthours(d, dateStart, dateEnd):
    # returns a 3rd rank tensor of data

    # initialize array
    circuits = range(13,25)
    numCircuits = len(circuits)
    numDays = (dateEnd - dateStart).days
    numHours = 24
    energy = np.zeros((numCircuits, numDays, numHours))

    # roundoff dates
    date = [datetime.datetime(dt.year, dt.month, dt.day, dt.hour) for dt in d['date']]
    date = np.array(date)

    for i,c in enumerate(circuits):
        # looks for date corresponding to time sample
        # if no date found, sample missing and previous sample used
        dateCurrent = dateStart
        lastWH = 0
        lastcredit = 0
        circuitIndex = c - circuits[0]
        dateIndex = 0
        while dateCurrent != dateEnd:
            data = d[date==dateCurrent]
            data = data[data['circuit_id']==c]
            hourIndex = dateCurrent.hour
            if data.shape == (0,):
                print 'no data', dateCurrent, c
                energy[circuitIndex, dateIndex, hourIndex] = lastWH
            elif data.shape[0] > 1:
                print 'too much data', dateCurrent, c
                energy[circuitIndex, dateIndex, hourIndex] = lastWH
            else:
                lastWH = data['watthours']
                lastcredit = data['credit']
                energy[circuitIndex, dateIndex, hourIndex] = data['watthours']
            dateCurrent += datetime.timedelta(hours=1)
            if dateCurrent.hour == 0:
                dateIndex += 1
    return energy

print('Begin Load Data')
d = getDataAsRecordArray(dateStart, dateEnd)
print('End Load Data')
printDataCompleteness(d)
plotHouseholdEnergyPerHour(d)
plotHouseholdEnergyPerDay(d)
plotTotalEnergyPerDay(d)
plotAllWattHours(d)
plotCreditSeparateAxes(d)
plotRecharges(d)
plotColloquium(d)


energy = sampleHourlyWatthours(d, dateStart, dateEnd)
plotAveragedAccumulatedHourlyEnergy(energy, dateStart, dateEnd)
plotAveragedHourlyEnergy(energy, dateStart, dateEnd)