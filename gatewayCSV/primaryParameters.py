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
dateStart = datetime.datetime(2011, 2, 05)
dateEnd = datetime.datetime.now()

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

def plotCredit(d):
    '''
    plots the credit in each circuit account
    '''
    fig = plt.figure()
    ax = fig.add_axes((0.15,0.2,0.7,0.7))
    circuits = set(d['circuit_id'])

    for i,c in enumerate(circuits):
        # assemble data by circuit
        circuitMask = d['circuit_id'] == c
        dates = matplotlib.dates.date2num(d[circuitMask]['date'])
        credit = d[circuitMask]['credit']

        # plot individual circuit data
        ax.plot_date(dates, credit,
                     '-o',
                     label = str(c),
                     color = plotColorList[i],
                     marker = plotSymbolList[i],
                     markeredgecolor = plotColorList[i],
                     markerfacecolor = 'None')

    # format plot and save
    dateFormatter = matplotlib.dates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(dateFormatter)
    ax.set_xlabel('Date')
    ax.set_ylabel('Credit in Account (FCFA)')
    ax.set_title('Account Credit in Pelengana')
    fig.autofmt_xdate()
    ax.legend(loc=(1.0,0.0))
    ax.grid()
    fig.savefig('plotCredit.pdf')

def plotRecharges(d):
    recharge = []

    circuits = set(d['circuit_id'])
    for i,c in enumerate(circuits):
        circuitMask = d['circuit_id'] == c
        dates = d[circuitMask]['date']
        credit = d[circuitMask]['credit']

        # pull out recharge events
        cd = np.diff(credit)
        cmask = cd > 0
        for element in zip(dates[cmask],cd[cmask]):
            recharge.append(element)

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
    fig = plt.figure()
    ax = fig.add_axes((0.15,0.2,0.7,0.7))

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
        ax.set_xlabel('Date')
        ax.set_ylabel('Energy Consumption (Watt-Hours)')
        ax.set_title('Hourly Accumulated Consumption Per Household')
        ax.legend(loc=(1.0,0.0))
        ax.grid()

        fig.savefig('plotHouseholdEnergyPerHour.pdf')

def plotHouseholdEnergyPerDay(d):

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



print('Begin Load Data')
d = getDataAsRecordArray(dateStart, dateEnd)
print('End Load Data')
#plotHouseholdEnergyPerHour(d)
#plotHouseholdEnergyPerDay(d)
#plotTotalEnergyPerDay(d)
#plotAllWattHours(d)
#plotCredit(d)
plotRecharges(d)
