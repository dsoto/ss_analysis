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

def getDataAsRecordArray():
    '''
    load csv from shared solar gateway and create
    numpy record array
    '''
    dtype = [('watthours',   'float'),      # column 0
             ('circuit_id',  'int'),        # column 5
             ('use_time',    'float'),      # column 6
             ('credit',      'float'),      # column 7
             ('circuit',     'S30'),        # column 8
             ('date',        'object')]     # column 9
    dtype = np.dtype(dtype)

    downloadFile = True

    # either get file from web or use existing file on computer
    fileName = 'PrimaryLog-data.csv'
    if os.path.isfile(fileName) and not downloadFile:
        # file exists so loadtxt uses csv file
        print 'loading', fileName
        print 'new data is _NOT_ being downloaded'
        print 'remove dataFile.csv to download fresh data'
        dataStream = open(fileName, 'r')
    else:
        # file does not exist so we must download it
        print 'opening url'
        import urllib
        dataString = urllib.urlopen('http://178.79.140.99/system/export?model=PrimaryLog').read()

        print 'converting to cStringIO'
        import cStringIO
        dataStream = cStringIO.StringIO(dataString)

        # dump csv data to file
        f = open('PrimaryLog-data.csv','w')
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

    # sort by date
    sortIndex = d['date'].argsort()
    d = np.take(d, sortIndex)

    return d

def plotCreditSeparateAxes(d, dateStart, dateEnd):
    '''
    plots the credit in each circuit account on a separate axis
    '''
    fig = plt.figure(figsize=(8,12))
    circuits = set(d['circuit_id'])
    circuits = range(13,25)
    d = d[(d['date'] > dateStart) & (d['date'] < dateEnd)]
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

def printRecharges(dateStart):
    '''
    reads in csv AddCredit data from gateway.
    outputs readable table of all credit purchases.
    outputs a second table of each household, total purchases, and purchase frequency.
    '''
    # define data headers for record array
    dtype = [('amount',      'float'),
             ('c1',          'S9'),
             ('c2',          'S4'),
             ('c3',          'S36'),
             ('c4',          'S30'),
             ('date',        'object'),
             ('cid',         'int'),
             ('active',      'S5'),
             ('c8',          'int')]
    dtype = np.dtype(dtype)

    # open url, download, convert to file-like object, and load into numpy record array
    import urllib
    dataString = urllib.urlopen('http://178.79.140.99/system/export?model=AddCredit').read()
    import cStringIO
    dataStream = cStringIO.StringIO(dataString)
    d = np.loadtxt(dataStream, delimiter=',',
                               skiprows=1,
                               dtype=dtype,
                               converters = {5: dateutil.parser.parse})

    # filter on dateStart
    data = d[d['date']>dateStart]

    # report table of recharges
    print
    print 'recharges since', dateStart.strftime('%Y-%m-%d')
    widths = (8,20,8)
    printTableRow(('circuit', 'date', 'amount'), widths)
    for d in data:
        printTableRow((d['cid']-12,
                       d['date'].strftime('%Y-%m-%d %H:%M'),
                       d['amount']),
                       widths)

    # system average daily income
    print
    print 'system average daily income'
    days = (datetime.datetime.now() - dateStart).days
    print sum(data['amount'])/days
    print

    # print out table by user/household
    circuits = list(set(data['cid']))
    circuits = range(13,25)
    circuits.sort()
    widths = (8, 8, 20)
    print 'total spent per circuit since', dateStart.strftime('%Y-%m-%d')
    printTableRow(('circuit','amount','recharge time interval (days)'), widths)
    for cir in circuits:
        recharges = data[data['cid']==cir]
        if recharges.shape == (0,):
            printTableRow((cir-12, '-', '-'), widths)
        else:
            timeBetweenRecharges = np.diff(recharges['date'])
            if timeBetweenRecharges.shape == (0,):
                avgTime = '-'
            else:
                timeBetweenRecharges = np.array([tbr.total_seconds() for tbr in timeBetweenRecharges])
                timeBetweenRecharges = timeBetweenRecharges / (24 * 60 * 60)
                avgTime = np.mean(timeBetweenRecharges)
                avgTime = '%0.1f' % avgTime

            printTableRow((cir-12,sum(recharges['amount']), avgTime), widths)

    print
    print 'data generated at',
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def plotRecharges(dateStart):
    '''
    plots recharge events and outputs statistics on recharges.
    inputs a CSV from the gateway AddCredit output, reads them into a numpy record array
    and then outputs on a plot.
    '''
    # define data headers for record array
    dtype = [('amount',      'float'),
             ('c1',          'S9'),
             ('c2',          'S4'),
             ('c3',          'S36'),
             ('c4',          'S30'),
             ('date',        'object'),
             ('cid',         'int'),
             ('active',      'S5'),
             ('c8',          'int')]
    dtype = np.dtype(dtype)

    # open url, download, convert to file-like object, and load into numpy record array
    import urllib
    dataString = urllib.urlopen('http://178.79.140.99/system/export?model=AddCredit').read()
    import cStringIO
    dataStream = cStringIO.StringIO(dataString)
    d = np.loadtxt(dataStream, delimiter=',',
                               skiprows=1,
                               dtype=dtype,
                               converters = {5: dateutil.parser.parse})

    # filter on dateStart
    data = d[d['date']>dateStart]

    recharge = []
    circuits = range(13,25)

    fig = plt.figure()
    ax = fig.add_axes((0.2, 0.2, 0.6, 0.6))

    dates = matplotlib.dates.date2num(data['date'])
    circuit = data['cid']
    credit = data['amount']

    ax.scatter(dates, circuit-12, s=credit/10,
                                                edgecolor = 'b',
                                                facecolor = 'None',
                                                color = 'None')
    ax.grid(True, linestyle='-', color = '#e0e0e0')
    ax.xaxis_date()
    ax.fmt_xdata = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))
    #fig.autofmt_xdate()
    ax.set_xlabel('Date')
    ax.set_ylabel('Circuit')
    ax.set_ylim((0,13))
    ax.set_yticks(range(1,13))
    ax.set_title('Recharge Purchases in Pelengana')
    annotation = 'plot generated - '
    annotation += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.02, 0.02, annotation)
    fig.savefig('plotRecharges.pdf')

def plotHouseholdEnergyPerHour(d, dateStart, dateEnd):
    '''
    plots a time series of accumulated watt hours
    for each circuit
    '''
    fig = plt.figure(figsize=(8,12))
    #ax = fig.add_axes((0.15,0.2,0.7,0.7))

    circuits = set(d['circuit_id'])
    circuits = range(13,25)

    d = d[(d['date'] > dateStart) & (d['date'] < dateEnd)]

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
    # fixme: this function has plot points that don't make sense
    '''
    for each date in d, sum watt hours and report
    '''
    # yank non-pelengana customer circuits
    d = d[d['circuit_id']!=25]     #MAINS pelengana
    d = d[d['circuit_id']!=28]
    d = d[d['circuit_id']!=29]
    d = d[d['circuit_id']!=30]

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

def plotAveragedHourlyEnergy(energy, dateStart, dateEnd):
    numCircuits = energy.shape[0]
    numDays     = energy.shape[1]
    numHours    = energy.shape[2]

    fig = plt.figure(figsize=(12,8))

    sy = 0.22
    sx = 0.15
    dx = sx * 1.4
    dy = sy * 1.3
    for i,c in enumerate(range(numCircuits)):
        x = (i % 4)
        y = 2 - (i / 4)
        ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))

        henergy = np.diff(energy[c], axis=1)
        henergy = np.hstack((energy[c, :, 0].reshape(numDays,1),henergy))

        for day in range(numDays):
            ax.plot(henergy[day],color='#dddddd')

        ax.plot(sum(henergy,0)/numDays,'k')
        ax.set_ylim((-5,50))
        ax.set_yticks((0,25,50))
        ax.set_xlim((0,23))
        ax.set_xticks((0,4,8,12,16,20,23))
        ax.text(0.4, 0.7, str(c+13), transform = ax.transAxes)
        ax.grid(True)
    fig.text(0.05, 0.7, 'Power Usage (W)', rotation='vertical')
    fig.suptitle('averaged power usage\n'+str(dateStart)+'\n'+str(dateEnd))
    fig.savefig('plotAveragedHourlyEnergy.pdf')

def printTableRow(strings, widths):
    for s,w in zip(strings, widths):
        print str(s).center(w),
    print

def plotAveragedAccumulatedHourlyEnergy(energy, dateStart, dateEnd):
    numCircuits = energy.shape[0]
    numDays     = energy.shape[1]
    numHours    = energy.shape[2]

    fig = plt.figure(figsize=(12,8))
    sy = 0.22
    sx = 0.15
    dx = sx * 1.4
    dy = sy * 1.3
    for i,c in enumerate(range(numCircuits)):
        x = (i % 4)
        y = 2 - (i / 4)
        ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))

        for day in range(numDays):
            ax.plot(energy[c, day, :],color='#dddddd')

        ax.plot(sum(energy[c],0)/numDays,'k')
        ax.set_ylim((0,160))
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

    dateCurrent = dateStart
    dateIndex = 0
    while dateCurrent != dateEnd:
        data = d[date==dateCurrent]
        hourIndex = dateCurrent.hour
        print dateCurrent,
        for i,c in enumerate(circuits):
            circuitIndex = c - circuits[0]
            loopData = data[data['circuit_id']==c]
            if loopData.shape == (0,):
                energy[circuitIndex, dateIndex, hourIndex] = energy[circuitIndex, dateIndex, hourIndex-1]
                print ' -',
            elif loopData.shape[0] > 1:
                energy[circuitIndex, dateIndex, hourIndex] = energy[circuitIndex, dateIndex, hourIndex-1]
                print ' +',
            else:
                energy[circuitIndex, dateIndex, hourIndex] = loopData['watthours']
                print c,
        print
        dateCurrent += datetime.timedelta(hours=1)
        if dateCurrent.hour == 0:
            dateIndex += 1

    return energy


if __name__ == '__main__':
    '''
    print('Begin Load Data')
    d = getDataAsRecordArray()
    print('End Load Data\n')

    dateStart = datetime.datetime(2011,  3,  3)
    dateEnd   = datetime.datetime(2011,  4,  1)
    #plotRecharges(d, dateStart, dateEnd)

    dateStart = datetime.datetime(2011,  3,  3)
    dateEnd   = datetime.datetime(2011,  4,  1)
    plotCreditSeparateAxes(d, dateStart, dateEnd)
    plotHouseholdEnergyPerHour(d, dateStart, dateEnd)
    #plotHouseholdEnergyPerDay(d)

    dateStart = datetime.datetime(2011,  3,  3)
    dateEnd   = datetime.datetime(2011,  3,  9)
    #dateEnd   = datetime.datetime.now()
    energy = sampleHourlyWatthours(d, dateStart, dateEnd)
    plotAveragedAccumulatedHourlyEnergy(energy, dateStart, dateEnd)
    plotAveragedHourlyEnergy(energy, dateStart, dateEnd)
'''
    dateStart = datetime.datetime(2011, 3, 3)
    printRecharges(dateStart)
    plotRecharges(dateStart)