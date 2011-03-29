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
    ''' take out values of None from the data on import.  used by getDataAsRecordArray.'''
    if val=='None':
        return 0.0
    else:
        val = float(val)
        if val < 0:
            val = 0
        return val

def getDataAsRecordArray(downloadFile = True):
    '''
    load csv from shared solar gateway and create
    numpy record array.
    if downloadFile==True, new data is downloaded from gateway.
    this function returns a numpy record array of data.
    '''
    usecols = [0,1,5,6,7,8,9]
    dtype = [('watthours',   'float'),      # column 0
             ('status',      'int'),        # column 1
             ('circuit_id',  'int'),        # column 5
             ('use_time',    'float'),      # column 6
             ('credit',      'float'),      # column 7
             ('circuit',     'S30'),        # column 8
             ('date',        'object')]     # column 9
    dtype = np.dtype(dtype)

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

def plotHouseholdEnergyPerHour(d, dateStart, dateEnd):
    '''
    plots a time series of accumulated watt hours
    for each circuit.
    displays plots in a 1x12 grid.
    output: plotHouseholdEnergyPerHour.pdf
    '''
    fig = plt.figure(figsize=(8,12))
    #ax = fig.add_axes((0.15,0.2,0.7,0.7))

    circuits = set(d['circuit_id'])
    circuits = range(13,26)

    d = d[(d['date'] > dateStart) & (d['date'] < dateEnd)]

    for i,c in enumerate(circuits):
        mask = d['circuit_id']==c
        dates = d[mask]['date']
        dates = matplotlib.dates.date2num(dates)
        wh = d[mask]['watthours']

        ax = fig.add_axes((0.15,0.1+i*0.065,0.7,0.05))

        # plot masked data to get date range
        ax.plot_date(dates, wh, '-x')
        ax.text(1.05, 0.4, c, transform = ax.transAxes)
        dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(dateFormatter)

        if i==0:
            ax.set_xlabel('Date')
        if i!=0:
            ax.set_xticklabels([])

        if i==12:
            ax.set_ylim((0,2000))
            ax.set_yticks((0,1000,2000))
        else:
            ax.set_ylim((0,150))
            ax.set_yticks((0,50,100,150))

    #fig.autofmt_xdate()
    fig.text(0.05,0.7, 'Energy Consumption (Watt-Hours)', rotation='vertical')
    fig.suptitle('Hourly Accumulated Consumption Per Household')
    fig.savefig('plotHouseholdEnergyPerHour.pdf')

def printPrimaryLogReports(d, dateStart, dateEnd):
    '''
    input:
    d - data array from getDataAsRecordArray,
    dateStart,
    dateEnd

    output:
    printPrimaryLogReports.txt

    this will loop through the report dates between dateStart and
    dateEnd and print which circuits are reporting at which times. the
    output is in tabular form to highlight missing SMS reports in the
    primary logs.
    '''
    print
    print 'printPrimaryLogReports - start'
    f = open('printPrimaryLogReports.txt','w')
    # get set of dates
    # filter on dateStart and dateEnd
    # loop through set of dates
    # print out circuits reporting
    dates = list(set(d['date']))
    dates.sort()
    dates = np.array(dates)
    dates = dates[(dates>dateStart)]
    for date in dates:
        f.write(str(date) + '   ')
        circuitsReporting = list(d[d['date']==date]['circuit_id'])
        circuitsReporting.sort()
        for circuit in range(13,31):
            if circuit in circuitsReporting:
                f.write(' ' + str(circuit))
            else:
                f.write('  -')
        f.write('\n')
    print 'printPrimaryLogReports - end'
    print

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

def printTableRow(strings, widths):
    '''
    this is a short helper function to write out a formatted row of a table.
    '''
    for s,w in zip(strings, widths):
        print str(s).center(w),
    print

def printTableRowLatex(strings, widths):
    '''
    this is a short helper function to write out a formatted row of a table.
    '''
    numColumns = len(zip(strings, widths))
    i = 0
    for s,w in zip(strings, widths):
        print str(s).center(w),
        if i <= numColumns - 2:
            print '&',
        i += 1
    print '\\\\'

def plotMultipleSeparateAxes(d, dateStart, dateEnd):
    '''
    plots the credit, watthours, status in each circuit account on a separate axis.
    i'm trying to see if people are turning their circuits off while they have
    credit in their accounts.
    currently in a 1x12 array.
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
        watthours = d[circuitMask]['watthours'] * 5
        status = d[circuitMask]['status'] * 1000

        # mask for status = 0 but credit > 0
        newMask = (status==0) & (credit>0)

        # plot individual circuit data
        if i == 0:
            ax = fig.add_axes((0.15,0.1+i*0.072,0.7,0.05))
        else:
            ax = fig.add_axes((0.15,0.1+i*0.072,0.7,0.05))
        ax.plot_date(dates[newMask], credit[newMask], '-x')
        ax.plot_date(dates[newMask], watthours[newMask], '-o')
        ax.plot_date(dates[newMask], status[newMask], '-d')
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
    fig.savefig('plotMultipleSeparateAxes.pdf')


# recharging and credit

def plotCreditSeparateAxes(d, dateStart, dateEnd):
    '''
    plots the credit in each circuit account on a separate axis.
    currently in a 1x12 array.
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
    print 'system average daily income (USD)'
    days = (datetime.datetime.now() - dateStart).days
    print '%.2f' % (sum(data['amount'])/days/500)
    print

    # print out table by user/household
    circuits = list(set(data['cid']))
    circuits = range(13,25)
    circuits.sort()
    widths = (8, 8, 30, 20)
    print 'total spent per circuit since', dateStart.strftime('%Y-%m-%d')
    printTableRow(('circuit','amount','recharge time interval (days)','monthly (USD)'), widths)
    for cir in circuits:
        recharges = data[data['cid']==cir]
        if recharges.shape == (0,):
            printTableRow((cir-12, '-', '-', '-'), widths)
        else:
            timeBetweenRecharges = np.diff(recharges['date'])
            if timeBetweenRecharges.shape == (0,):
                avgTime = '-'
            else:
                timeBetweenRecharges = np.array([tbr.total_seconds() for tbr in timeBetweenRecharges])
                timeBetweenRecharges = timeBetweenRecharges / (24 * 60 * 60)
                avgTime = np.mean(timeBetweenRecharges)
                avgTime = '%0.1f' % avgTime
            total = sum(recharges['amount'])
            monthly = total / days * 30 / 500
            monthly = '%.2f' % monthly
            printTableRow((cir-12, total, avgTime, monthly), widths)

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
    circuit = np.array(map(float, data['cid'])) - 12
    # adding random number to see overlapping data points
    import random
    circuit = [c + (random.random() - 0.5) * .25 for c in circuit]
    credit = data['amount']

    ax.scatter(dates, circuit, s=credit/10,
                                                edgecolor = 'b',
                                                facecolor = 'None',
                                                color = 'None')
    ax.grid(True, linestyle='-', color = '#e0e0e0')
    ax.xaxis_date()
    ax.fmt_xdata = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()
    ax.set_xlabel('Date')
    ax.set_ylabel('Circuit')
    ax.set_ylim((0,13))
    ax.set_yticks(range(1,13))
    ax.set_title('Recharge Purchases in Pelengana')
    annotation = 'plot generated - '
    annotation += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.02, 0.02, annotation)
    fig.savefig('plotRecharges.pdf')


# aggregated by day

def parseTotalEnergyPerDay(d, dateStart, dateEnd):
    '''
    create array of energy use per circuit for a group of circuits.
    returns a numpy array with
    axis 0 - date
    axis 1 - circuit
    and each value is the daily energy used by each circuit for that date.
    the daily usage is determined by taking the last valid watthours report for
    each date in the range dateStart, dateEnd
    '''

    # initialize array
    circuits = range(13,26)
    numCircuits = len(circuits)
    numDays = (dateEnd - dateStart).days + 1
    energy = np.zeros((numDays, numCircuits))

    # loop through and populate array with energy values
    todayStart = dateStart
    dateIndex = 0
    while todayStart <= dateEnd:
        todayEnd = todayStart + datetime.timedelta(days=1)
        for circuit in range(13,26):
            circuitIndex = circuit - 13
            # filter data down to a single day and circuit and then
            # find the last of these samples for the day's energy
            data = d
            data = data[data['circuit_id']==circuit]
            if data.shape == (0,):
                print 'no circuit data for ', todayStart
            else:
                data = data[(data['date']>todayStart) & (data['date']<todayEnd)]
            if data.shape == (0,):
                print 'no date data for', todayStart
            else:
                lastSampleDate = data['date'].max()
                #print lastSampleDate,
                thisSample = data[data['date']==lastSampleDate]['watthours']
                #print dateIndex, circuitIndex
                energy[dateIndex, circuitIndex] = thisSample
        todayStart = todayEnd
        dateIndex += 1
    return energy

def printTotalEnergyPerDay(d, dateStart, dateEnd):
    energy = parseTotalEnergyPerDay(d, dateStart, dateEnd)

    # make date range from dateStart and dateEnd
    plotDates = matplotlib.dates.drange(dateStart,
                                        dateEnd+datetime.timedelta(days=1),
                                        datetime.timedelta(days=1))
    print
    print 'Date'.center(12),
    for i in range(1,13):
        print str(i).center(8),
    print 'Mains'.center(8)
    for i,e in enumerate(energy):
        print matplotlib.dates.num2date(plotDates[i]).strftime('%Y-%m-%d').center(12),
        for entry in e:
            print str(entry).center(8),
        print
    print
    print 'mean'.center(12),
    for i in range(0,13):
        print ('%.1f' % energy[:,i].mean()).center(8),
    print

    print 'std'.center(12),
    for i in range(0,13):
        print ('%.1f' % energy[:,i].std()).center(8),

def plotTotalEnergyPerDayByCircuit(d, dateStart, dateEnd):
    energy = parseTotalEnergyPerDay(d, dateStart, dateEnd)

    # make date range from dateStart and dateEnd
    plotDates = matplotlib.dates.drange(dateStart,
                                        dateEnd+datetime.timedelta(days=1),
                                        datetime.timedelta(days=1))

    fig = plt.figure(figsize=(12,8))

    # size y and size x of plot
    sy = 0.15
    sx = 0.15
    # spacing for x and y
    dx = sx * 1.4
    dy = sy * 1.5
    numCircuits = 13
    for i,c in enumerate(range(numCircuits)):
        x = (i % 4)
        y = 3 - (i / 4)
        ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))
        ax.plot_date(plotDates, energy[:,i],'x-k')
        # set the plot to have 3 major ticks with month-day format
        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=len(plotDates)/3))
        ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))
        if i == 12:
            ax.set_ylim((0,2000))
            ax.set_title('Total Consumption')
        else:
            ax.set_title('Household ' + str(c + 1))
            ax.set_ylim((0,150))
            ax.set_yticks((0,50,100,150))

    x = 1
    y = 0
    ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))
    ax.plot_date(plotDates, energy[:,:11].sum(1),'x-k')
    ax.set_title('All Households')
    ax.set_ylim((0,2000))
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=len(plotDates)/3))
    ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))

    x = 2
    y = 0
    ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))
    ax.plot_date(plotDates, energy[:,12]-energy[:,:11].sum(1),'x-k')
    ax.set_title('Meter Consumption')
    ax.set_ylim((0,2000))
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=len(plotDates)/3))
    ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))

    fig.suptitle('Pelengana Energy Consumption')
    fig.autofmt_xdate()
    fig.savefig('plotTotalEnergyPerDayByCircuit.pdf')


# averaging functions

def sampleHourlyWatthours(d, dateStart, dateEnd):
    '''
    attempts to create a common time base of watthour data from csv file.
    watt hour data that is not present is replaced by the previous sample.
    fixme - i don't know what happens when we send two reports at 23:xx.
    returns a 3rd rank tensor of data.
    '''

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
                # if sample not present, replace with previous sample
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

def plotAveragedHourlyPower(energy, dateStart, dateEnd):
    '''
    by sampling the watt hour reporting from the gateway to a common time base,
    this function can report the average hourly energy use over a series of days
    ranging from dateStart to dateEnd.
    in this case the energy curve is differentiated to provide a power curve.
    average energy is reported on a separate axes for each household with the
    average depicted in black and each daily curve in grey.
    '''
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
    fig.savefig('plotAveragedHourlyPower.pdf')

def plotAveragedAccumulatedHourlyEnergy(energy, dateStart, dateEnd):
    '''
    uses hourly sampled watt hour reporting from the gateway, this function charts the
    averaged accumulated energy profile.
    average energy shown in black, individual plots are shown in grey.
    '''
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

def plotWindowAveragedWatthoursByCircuit(d, dateStart, dateEnd):
    '''
    unfinished.
    this function plots an averaged daily load curve based on a range of
    data between dateStart and dateEnd.
    Data is published for each household and for the mains.
    '''
    d = d[(d['date'] > dateStart) & (d['date'] < dateEnd)]

    fig = plt.figure(figsize=(12,8))

    # spacing for x and y
    dx = 0.20
    dy = 0.22
    # size y and size x of plot
    sx = dx * 0.8
    sy = dy * 0.75

    numCircuits = 13
    totalAveragedEnergy = np.zeros(25)
    for i,c in enumerate(range(numCircuits)):
        x = (i % 4)
        y = 3 - (i / 4)
        ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))

        thisData = d[d['circuit_id']==c+13]
        thisTime = np.array([tt.hour + tt.minute/60. for tt in thisData['date']])

        averagedEnergy = np.zeros(25)
        for i in range(1,25):
            timeMask = (thisTime < i) & (thisTime > i-1)
            averagedEnergy[i] = thisData[timeMask]['watthours'].mean()

        ax.plot(thisTime, thisData['watthours'],'x', color = '#d0d0d0')
        ax.plot(range(0,25), averagedEnergy, 'x-k')
        if c == 12:
            ax.set_ylim((0,2000))
            ax.set_title('Total Consumption')
        else:
            totalAveragedEnergy += averagedEnergy
            ax.set_title('Household ' + str(c + 1))
            ax.set_ylim((0,150))
            ax.set_yticks((0,50,100,150))
        ax.set_xlim(0,24)
        ax.set_xticks((0,6,12,18,24))

    i = 13
    x = (i % 4)
    y = 3 - (i / 4)
    ax = fig.add_axes((0.10 + x*dx, 0.05 + y*dy, sx, sy))
    ax.plot(range(0,25), totalAveragedEnergy, 'x-k')
    ax.set_ylim((0,1000))
    ax.set_title('Household Consumption')
    ax.set_xlim(0,24)
    ax.set_xticks((0,6,12,18,24))

    fig.suptitle('Averaged Accumulated Energy Consumption\n' +
                  dateStart.strftime('%Y-%m-%d') + ' to ' + dateEnd.strftime('%Y-%m-%d') +
                  '\nWatthours vs. Time of Day')
    fig.savefig('plotWindowAveragedWatthours.pdf')

# deprecated

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

def plotTotalEnergyPerDay235959(d, dateStart, dateEnd):
    '''
    uses 23:59:59 timestamps to calculate and report sum of all energy
    consumed by all households each day.  checks to see if all circuits
    are reporting.  if circuit is not reporting, its share of the energy
    is replaced by the average of all households.
    this method can only be used for data on or after feb 28, 2011 when we
    started reporting a day-end report of watthours.
    output -
    plotHouseholdEnergyPerDay.pdf

    '''
    dateStart = datetime.datetime(dateStart.year,
                                  dateStart.month,
                                  dateStart.day,
                                  23,
                                  59,
                                  59)
    dateCurrent = dateStart
    dailyEnergy = []
    dateList = []
    # drop circuits 25, 28, 29, 30
    dropCircuits = [25, 28, 29, 30]
    for dropCircuit in dropCircuits:
        d = d[d['circuit_id']!=dropCircuit]

    while dateCurrent <= dateEnd:
        print dateCurrent,
        dataCurrent = d[d['date']==dateCurrent]
        #print dataCurrent.shape
        circuits = dataCurrent['circuit_id']
        circuits.sort()
        if len(circuits) < 12:
            print 'not all reporting',
        #print circuits
        currentEnergy = np.mean(dataCurrent['watthours'])*12
        dailyEnergy.append(currentEnergy)
        reportDate = datetime.datetime(dateCurrent.year,
                                       dateCurrent.month,
                                       dateCurrent.day)
        dateList.append(reportDate)
        print currentEnergy
        #print sum(dataCurrent['watthours'])
        dateCurrent += datetime.timedelta(days=1)

    print dailyEnergy

    fig = plt.figure()
    ax = fig.add_axes((0.15,0.2,0.7,0.7))

    dateList = matplotlib.dates.date2num(dateList)

    ax.plot_date(dateList, dailyEnergy, '-x')
    fig.autofmt_xdate()
    ax.set_ylim(bottom=0)
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy Consumption (Wh)')
    ax.set_title('Household Energy Consumption Per Day')
    fig.savefig('plotTotalEnergyPerDay235959.pdf')

def plotTotalEnergyPerDay23xxxx(d, dateStart):
    '''
    this is very similar to plotHouseholdEnergyPerDay but uses any 23 timestamped
    data to get the day end.  this leads to duplicate data points for many dates.
    plot energy consumed by all circuits for each day
    not including mains
    '''
    dropCircuits = [25, 28, 29, 30]
    for dropCircuit in dropCircuits:
        d = d[d['circuit_id']!=dropCircuit]

    d = d[d['date']>dateStart]
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

    fig.savefig('plotTotalEnergyPerDay23xxxx.pdf')

def plotTotalEnergyPerDay(d, dateStart, dateEnd):
    '''
    '''

    energy = parseTotalEnergyPerDay(d, dateStart, dateEnd)

    # make date range from dateStart and dateEnd
    plotDates = matplotlib.dates.drange(dateStart,
                                        dateEnd+datetime.timedelta(days=1),
                                        datetime.timedelta(days=1))

    fig = plt.figure()
    ax = fig.add_subplot(111)

    householdsTotal = energy[:,:11].sum(1)
    mains = energy[:,12]
    system = mains - householdsTotal

    ax.plot_date(plotDates, householdsTotal, 'x-k', label='Household')
    ax.plot_date(plotDates, system, 'x-b', label='Meter consumption')
    ax.plot_date(plotDates, mains, 'x-g', label='Mains')
    ax.legend(loc='best')
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    fig.autofmt_xdate()

    ax.grid()
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (Watt-Hours)')
    ax.set_ylim(bottom=0)
    ax.set_title('Total Household Energy Consumed Per Day')

    fig.savefig('plotTotalEnergyPerDay.pdf')


if __name__ == '__main__':

    print('Begin Load Data')
    d = getDataAsRecordArray()
    print('End Load Data\n')

    flag = False
    if flag:
        dateStart = datetime.datetime(2011,  3,  3)
        dateEnd   = datetime.datetime(2011,  4,  1)
        #plotRecharges(d, dateStart, dateEnd)

    flag = False
    if flag:
        dateStart = datetime.datetime(2011,  2,  14)
        dateEnd   = datetime.datetime(2011,  3,  12)
        #plotCreditSeparateAxes(d, dateStart, dateEnd)
        plotHouseholdEnergyPerHour(d, dateStart, dateEnd)
        plotHouseholdEnergyPerDay(d, dateStart, dateEnd)
        plotTotalEnergyPerDay(d, dateStart)
        printPrimaryLogReports(d, dateStart, dateEnd)

    flag = False
    if flag:
        dateStart = datetime.datetime(2011,  3,  3)
        dateEnd   = datetime.datetime(2011,  3,  12)
        #dateEnd   = datetime.datetime.now()
        energy = sampleHourlyWatthours(d, dateStart, dateEnd)
        plotAveragedAccumulatedHourlyEnergy(energy, dateStart, dateEnd)
        plotAveragedHourlyEnergy(energy, dateStart, dateEnd)

    flag = False
    if flag:
        dateStart = datetime.datetime(2011, 3, 3)
        printRecharges(dateStart)
        plotRecharges(dateStart)

    dateStart = datetime.datetime(2011,2,1)
    dateEnd = datetime.datetime(2011,3,14)
    energy = parseTotalEnergyPerDay(d, dateStart, dateEnd)