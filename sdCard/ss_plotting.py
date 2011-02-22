import os
import numpy as np
import dateutil.parser
import matplotlib.dates
import datetime
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import datetime
import scipy.integrate

verbose = 0
numColumns = 20
#dateRangeStart = datetime.datetime(2010, 12, 20)
dateRangeStart = datetime.datetime(2011, 1, 24)
dateRangeEnd = datetime.datetime(2011, 2, 17)

# helper functions
# ----------------

def getFormattedData(circuit, beginDatetime, endDatetime, downsample, dataDirectory):
    '''
    read in data from directories from begin date to end date
    and return numpy record array
    '''
    list = [('Time Stamp',       'S14'),
            ('Watts',            'float'),
            ('Volts',            'float'),
            ('Amps',             'float'),
            ('Watt Hours SC20',  'float'),
            ('Watt Hours Today', 'float'),
            ('Max Watts',        'float'),
            ('Max Volts',        'float'),
            ('Max Amps',         'float'),
            ('Min Watts',        'float'),
            ('Min Volts',        'float'),
            ('Min Amps',         'float'),
            ('Power Factor',     'float'),
            ('Power Cycle',      'float'),
            ('Frequency',        'float'),
            ('Volt Amps',        'float'),
            ('Relay Not Closed', 'float'),
            ('Send Rate',        'float'),
            ('Machine ID',       'float'),
            ('Type',             'S8'),
            ('Credit',           'float')]
    typeCircuit = np.dtype(list)
    typeMains = np.dtype(list[0:-1])

    if '200' in circuit:
        type = typeMains
    else:
        type = typeCircuit

    currentDatetime = beginDatetime
    data = []
    while currentDatetime != endDatetime:
        # construct path for certain hour of data
        path  = str(currentDatetime.year) + '/'
        path += str(currentDatetime.month) + '/'
        path += str(currentDatetime.day) + '/'
        path += str(currentDatetime.hour)
        path = '%02d/%02d/%02d/%02d/' % (currentDatetime.year,
                                         currentDatetime.month,
                                         currentDatetime.day,
                                         currentDatetime.hour)
        filename = '192_168_1_' + circuit + '.log'
        file = dataDirectory + path + filename

        if verbose == 1:
            print 'reading ' + file

        # read log file
        if os.path.isfile(file):
            newData = np.loadtxt(file, delimiter=',', dtype = type, skiprows = 1)
            # if newData is only one line it is a pita so discard it
            # fixme: figure out how to append these one line logs
            if newData.shape != ():
                if data == []:
                    data = newData
                else:
                    data = np.append(data, newData, axis=0)

        # increment by one hour
        currentDatetime = currentDatetime + datetime.timedelta(hours=1)

    return data

def getData(plotCircuit, plotDate, downsample, dataDirectory):
    '''
    deprecated function to get data that used os.walk
    '''
    if verbose == 1:
        print 'getting data for', plotCircuit, plotDate
    data = []
    directoryToWalk = dataDirectory + '/' + plotDate
    if verbose == 1:
        print directoryToWalk
    for dirname, dirnames, filenames in os.walk(directoryToWalk):
        if verbose == 1:
            print dirname, dirnames, filenames
        for filename in filenames:
            if plotCircuit in filename:
                if verbose == 1:
                    print 'getting data for', dirname
                # usecols = [crap] is a hideous hack to avoid text string column
                if verbose == 1:
                    print dirname + '/' + filename
                if '200' in plotCircuit:
                    usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                               11, 12, 13, 14, 15, 16, 17, 18]
                    numColumns = len(usecols)
                else:
                    usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 20]
                    numColumns = len(usecols)
                tempData = np.loadtxt(dirname + '/' + filename,
                                      usecols = usecols,
                                      delimiter = ',',
                                      skiprows = 1)

                # deal with case of one line file
                if data == []:
                    data = tempData
                    if data.shape == (numColumns,):
                        data = data.reshape(1,numColumns)
                elif tempData.shape == (numColumns,):
                    tempData = tempData.reshape(1,numColumns)
                else:
                    data = np.append(data, tempData, axis=0)
    # check for nonexistent data
    if data != []:
        # decimate data by skipping 'downsample' samples
        index = range(0, data.shape[0], downsample)
        data = data[index]
    if verbose == 1:
        print data
    return data

def getHeaderStrings():
    '''deprecated function to get header strings for SC20 data'''
    d = {}
    headers = ['Time Stamp',
               'Watts',
               'Volts',
               'Amps',
               'Watt Hours SC20',
               'Watt Hours Today',
               'Max Watts',
               'Max Volts',
               'Max Amps',
               'Min Watts',
               'Min Volts',
               'Min Amps',
               'Power Factor',
               'Power Cycle',
               'Frequency',
               'Volt Amps',
               'Relay Not Closed',
               'Send Rate',
               'Machine ID',
               'Credit']
    for i,h in enumerate(headers):
        d[i]=h
    return d

def resampleData(data, column, dateStart, dateEnd, dt):
    '''
    given a numpy record array and dateStarts and ends and a timestep
    this function will place samples of data on evenly spaced timesteps
    and will attempt to do the right thing in areas with no data
    '''
    # parsedDates are datetime objects
    if verbose == 1:
        print 'parsing dates'
    parsedDates = [dateutil.parser.parse(t) for t in data['Time Stamp']]
    # mplDates are days
    mplDates = matplotlib.dates.date2num(parsedDates)


    oldSeconds = [(date - dateStart).days * 86400 +
                  (date - dateStart).seconds for date in parsedDates]

    # loop through newSeconds and find new values
    # for power, if no neighboring value, power = 0
    # make newSeconds deal with dateStart and dateEnd
    totalSeconds = (dateEnd - dateStart).days * 86400 + (dateEnd - dateStart).seconds
    newSeconds = np.arange(0, totalSeconds+1, dt)

    newPower = np.zeros(len(newSeconds))
    threshold = dt

    if column == 'Watts':
        findMethod = 1
        if findMethod == 0:
            if verbose == 1:
                print 'finding samples brute force'
            for i, second in enumerate(newSeconds):
                # find nearest oldSeconds sample
                delta = min(abs(oldSeconds - second))
                index = np.argmin(abs(oldSeconds - second))
                if delta < 15:
                    newPower[i] = data[column][index]

        if findMethod == 1:
            # this section does not work yet
            if verbose == 1:
                print 'finding samples indexing'
            ind = 0
            for i, sec in enumerate(newSeconds):
                while 1:
                    if ind == len(oldSeconds) -1:
                        newPower[i] = 0
                        break
                    dt1 = abs(oldSeconds[ind]-sec)
                    dt2 = abs(oldSeconds[ind+1]-sec)
                    if dt2 > dt1:
                        if dt1 < threshold:
                            newPower[i] = data[column][ind]
                        else:
                            newPower[i] = 0
                        break
                    ind += 1
    else:
        ind = 0
        for i, sec in enumerate(newSeconds):
            while 1:
                if ind == len(oldSeconds) -1:
                    newPower[i] = newPower[i-1]
                    break
                dt1 = abs(oldSeconds[ind]-sec)
                dt2 = abs(oldSeconds[ind+1]-sec)
                if dt2 > dt1:
                    if dt1 < threshold:
                        newPower[i] = data[column][ind]
                    else:
                        if i == 0:
                            newPower[i] = 0
                        else:
                            newPower[i] = newPower[i-1]
                    break
                ind += 1

    # convert newSeconds to datetime objects
    newTime = []
    for second in newSeconds:
        deltaDays = second / 86400
        deltaSeconds = second % 86400
        newTime.append(dateStart+ datetime.timedelta(days = int(deltaDays),
                                                     seconds = int(deltaSeconds)))


    if verbose == 1:
        print 'returning result'
    return newTime, newPower

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
    #axis.set_ylim((0, 1000))
    fig.autofmt_xdate()


# output csv functions
# --------------------

def writeDailyUsageCSV():
    data = calculateDailyUsage()
    pass

def calculateDailyUsage():
    '''
    creates csv-like output to stdout with daily usage over a range of
    days.  also creates graph of usage.  and a histogram
    TODO : make this compare against existing CSV of usage and grab data that isn't in file
    '''
    #import ss_plotting as ssp

    dataDirectory = './data/'
    plotCircuitList = ['200','201','202','203','204','205','206','207','208','209','210','211','212']
    #plotCircuitList = ['201','202','203','204','205','206','207','208','209','210','211','212']
    totalPower = []

    # loop through days
    # for each day compute total use and store in array
    days = (dateRangeEnd - dateRangeStart).days
    days = range(days)

    #print header
    print 'date,',
    for circuit in plotCircuitList:
        print circuit.rjust(5)+',',
    print

    dayRange = []
    individualWattHours = []
    totalWattHours = []
    scWattHours = []
    scDataList = []
    for day in days:
        dateStart = dateRangeStart + datetime.timedelta(days=day)
        dateEnd = dateStart + datetime.timedelta(days=1)
        totalWattHoursForDay = 0
        print str(dateStart.year) + '/' + str(dateStart.month) + '/' + str(dateStart.day) + ',',
        for circuit in plotCircuitList:
            data = getFormattedData(circuit, dateStart, dateEnd, 1, dataDirectory)
            if data == []:
                #print 'no data for', dateStart, circuit
                integral = 0
                scwht = 0
            else:
                #dts = map(dateutil.parser.parse,data['Time Stamp'])
                #mpldays = matplotlib.dates.date2num(dts)
                #integral = scipy.integrate.trapz(data['Watts'],dx=3.0/60/60)
                scwht = data['Watt Hours Today'][-1]

            totalWattHoursForDay += scwht
            #print dateStart.month, dateStart.day, circuit, integral
            #print dateStart.month, dateStart.day, circuit, scwht
            print str(scwht).rjust(5) + ',',
            individualWattHours.append(scwht)

        print
        #print totalWattHoursForDay
        dayRange.append(dateStart)
        totalWattHours.append(totalWattHoursForDay)

    # line plot of total system usage
    mpldays = matplotlib.dates.date2num(dayRange)
    fig, axis = getFigure()
    axis.plot_date(dayRange, totalWattHours,'-')
    formatFigure(fig, axis)
    fig.savefig('3.pdf')


    plotHistogram(individualWattHours)

def writeHourlyUsageCSV():
    '''
    write csv with hourly watt-hour consumption of all circuits
    over a given date range
    '''
    pass

# plotting functions
# ------------------

def plotHistogram(individualWattHours):
    '''
    plot histogram of all daily usage
    histogram plotting function called by calculateDailyUsage
    '''
    bins = 50
    range = (0,200)
    fig, axis = getFigure()
    axis.hist(individualWattHours, bins=bins, range=range)
    axis.set_xlabel('Watt-Hours Consumed')
    axis.set_ylabel('Days')
    axis.set_title('Daily Consumption at Pelengana Site')
    fig.savefig('3_hist.pdf')

def stackedConsumption():
    import numpy as np
    import matplotlib.pyplot as plt
    # todo: load in dates as well and plot dates?
    d = np.loadtxt('dailyUsagePelengana.csv',
                    usecols=range(1,13),
                    skiprows=1,
                    dtype=np.float,
                    delimiter=',')
                 # remove days with 0 consumption by masking array
    mask = d == 0.0
    rowsNonZero = ~mask.any(1)
    i = 0
    for row in rowsNonZero:
        if not row:
            i+=1
    print i, 'rows dropped'
    d = d[rowsNonZero, :]

    stackedData = d.cumsum(1)
    x = range(d.shape[0])
    color = [(0.9,0.9,0.9),
             (0.7,0.7,0.7),
             (0.5,0.5,0.5)]
    for i in range(d.shape[1]):

        if i == 0:
            plt.fill_between(x,np.zeros(len(stackedData[:,i])), stackedData[:,i],color = color[i % 3])
        else:
            plt.fill_between(x, stackedData[:,i-1], stackedData[:,i], color = color[i % 3])
        '''
        plt.plot(stackedData[:,i])
        '''
    #plt.show()
    plt.title('Stacked Plot of Pelengana Consumption')
    plt.xlabel('Day')
    plt.ylabel('Energy Consumed')
    plt.savefig('stackedConsumption.pdf')
    plt.close()

def usageBarGraph():
    '''
    using csv file created from calculateDailyUsage(), we look at statistics
    on usage among the residents
    '''
    import numpy as np

    d = np.loadtxt('dailyUsagePelengana.csv',
                    usecols=range(1,13),
                    skiprows=1,
                    dtype=np.float,
                    delimiter=',')

    # remove days with 0 consumption by masking array
    mask = d == 0.0
    rowsNonZero = ~mask.any(1)
    i = 0
    for row in rowsNonZero:
        if not row:
            i+=1
    print i, 'rows dropped'
    d = d[rowsNonZero, :]

    mean = d.mean(0)
    std = d.std(0)

    mean = np.append(mean, d.mean())
    std = np.append(std, d.std())

    locations = np.arange(13)
    ticks = map(str, np.arange(12) + 1)
    ticks.append('AVG')
    tickLoc = locations + 0.4
    # create bar chart with error bars
    import matplotlib.pyplot as plt
    plt.bar(locations, mean, yerr=std, color=(0.9,0.9,0.9), ecolor='k')
    plt.xticks(tickLoc, ticks)
    plt.xlim((-0.5,13.5))
    plt.xlabel('Household')
    plt.ylabel('Daily Average Energy Usage (Wh)')
    plt.title('Pelengana January Power Consumption')
    #plt.show()
    plt.savefig('pelenganaConsumption.pdf')

def plotLoadDurationCurve():
    '''
    takes data from start to end dates, tabulates power usage, and generates
    a load duration curve that orders hours vs power
    '''
    # open hourly usage csv file
    # loop through and calculate overall system usage for each hour
    # sort usage by magnitude
    # plot
    pass