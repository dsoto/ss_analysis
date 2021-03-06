# uses python 2.7.1
import urllib
import numpy as np                # version 1.5.1
import matplotlib.dates           # version 1.0.1
import matplotlib.pyplot as plt   # version 1.0.1
import datetime as dt

# setup logging
import twiggy as tw
tw.quickSetup(file='sql_analysis.log')
tw.log.info('loading analysis.py')

# circuit id's for quick and dirty lists
mali001 = range(13,25)
ml01 = range(13, 25)
ml05 = [56, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 77, 93, 95]
#ml06 = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 96, 97, 98, 99, 100]
ml06 = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 96, 97]
uganda002 = range(33, 41) + range(42, 48) + range(49, 56) + [101]

today = dt.datetime.now()
dateEnd = dt.datetime(today.year, today.month, today.day) - dt.timedelta(days=1)
dateStart = dateEnd - dt.timedelta(days=6)
may_15 = dt.datetime(2011,5,15)
jun_15 = dt.datetime(2011,6,15)

# rcparams ----------------------------
import matplotlib as mpl
mpl.rcParams['font.family']     = 'serif'
mpl.rcParams['font.size']       = 8
mpl.rcParams['axes.labelsize']  = 14
mpl.rcParams['axes.titlesize']  = 14
mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12

# XFCA to USD
toUSD = 1.0/500

# this may need to change depending on where you are running this script from
import sys
# if importing 'import sql.daniel as d' from ss_analysis directory
sys.path.append('../gateway_env/gateway/gateway/')

from models import *
#--------------------------------------------------------------------------------------------#
# convenience and helper functions

def printJobs():
    #jobs = session.query(Job).filter(Job.circuit_id == 14)
    jobs = session.query(Job).filter(Job._type == 'addcredit').filter(Job.circuit_id ==14)
    for j in jobs:
        print j

'''
this is a short helper function to write out a formatted row of a table.
'''
def printTableRow(strings, widths):
    for s,w in zip(strings, widths):
        print str(s).rjust(w),
    print

'''
this is a short helper function to write out a formatted row of a table in LaTeX format.
'''
def printTableRowLatex(strings, widths):
    numColumns = len(zip(strings, widths))
    i = 0
    for s,w in zip(strings, widths):
        print str(s).center(w),
        if i <= numColumns - 2:
            print '&',
        i += 1
    print '\\\\'

'''
convenience function to return a list of integers representing the circuits
associated with a meter
'''
def getCircuitsForMeter(mid):
    circuits = session.query(Circuit).filter(Circuit.meter_id == mid).order_by(Circuit.id)
    circuits = [c.id for c in circuits]
    return circuits


# plotting functions

'''
this function reports the consistency of primary logs in graphical form
'''
def plotMeterMessagesByCircuit(report, dates):
    for i, meter_id in enumerate([4,6,7,8]):
        meterCircuits = session.query(Circuit).filter(Circuit.meter_id == meter_id)
        meterName = session.query(Meter).filter(Meter.id == meter_id)[0].name
        print 'generating for ', meterName

        meterCircuits = [mc.id for mc in meterCircuits]
        meterCircuits.sort()
        print meterCircuits

        startDate = dates[0]
        endDate = dates[-1]
        meterReport = report[:,meterCircuits]

        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(meterReport.sum(0) / meterReport.shape[0],'x')
        ax.set_title(meterName+'\nFrom '+startDate.strftime('%Y-%m-%d')+' to '+
                                         endDate.strftime('%Y-%m-%d'))
        ax.set_ylim((0,1))
        ax.set_xlabel('circuit index (not well ordered)')
        ax.set_ylabel('Percentage of time reporting')
        fig.savefig('uptime_by_circuit_'+meterName+'.pdf')
        plt.close()

def plotDailyTotalWattHoursForAllCircuitsOnMeter(meter_id,
                                                 dateStart=dt.datetime(2011,4,1),
                                                 dateEnd=dt.datetime(2011,5,18),
                                                 showMains=True):
    for i,mid in enumerate(meter_id):
        circuits = getCircuitsForMeter(mid)

        # drop mains circuit
        for c in circuits:
            if session.query(Circuit).filter(Circuit.id == c)[0].ip_address == '192.168.1.200':
                circuits.remove(c)

        #fig, ax = plt.subplots(len(circuits), 1, sharex = True, figsize=(5,15))
        if len(circuits) > 12:
            fig, ax = plt.subplots(4, 5, sharex = False, figsize=(11,8.5))
            stride = 4
        else:
            fig, ax = plt.subplots(4, 3, sharex = False, figsize=(10,8))
            stride = 4

        for i,c in enumerate(circuits):
            # fetch data
            dates, watthours = getDailyEnergyListForCircuit(c, dateStart, dateEnd)

            # filter based on greater than or equal zero consumption (neg is error)
            mask = watthours > 0
            dates = dates[mask]
            watthours = watthours[mask]

            dates = matplotlib.dates.date2num(dates)
            thisAxes = ax[i % stride, i / stride]
            thisAxes.plot_date(dates, watthours, ls='-', ms=3, marker='o', mfc=None)
            #thisAxes.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=(0)))
            #thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
            thisAxes.text(0.7,0.7,str(c),transform = thisAxes.transAxes)

            thisAxes.set_ylim((0,150))
            thisAxes.set_yticks((0,50,100,150))
            #ax[i].set_title(titleString)
            #ax[i].grid(True)

        fileNameString = 'meter' + str(mid) + 'daily energy.pdf'
        fig.suptitle(fileNameString)
        fig.autofmt_xdate()
        fig.savefig(fileNameString)


#--------------------------------------------------------------------------------------------#
# plotting functions


def plotDatasForCircuit(circuit_id,
                        dateStart=dt.datetime(2011,10,20),
                        dateEnd=dt.datetime(2011,10,24),
                        quantity=('watthours','credit'),
                        titleString=None,
                        introspect=False):
    '''
    plots multiple quantities on a plot for printing and introspection
    '''
    # set subplots for length of quantity
    numPlotsX = 1
    numPlotsY = len(quantity)

    # plot, figure and axes creation
    fig = plt.figure()
    fig, axs = plt.subplots(numPlotsY, numPlotsX, sharex=True)

    # iterate through quantity
    for i,q in enumerate(quantity):
        dates, data = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity=q)
        dates = matplotlib.dates.date2num(dates)
        thisAxes = axs[i]
        thisAxes.plot_date(dates, data, ls='-', c='#eeeeee', ms=6, marker='o', mfc=None)
        thisAxes.set_title(q)
        thisAxes.grid(linestyle='-', color='#eeeeee')
        thisAxes.set_xlim((matplotlib.dates.date2num(dateStart),
                           matplotlib.dates.date2num(dateEnd)))

    # add annotation on plot of circuit ip and meter name
    annotation = []
    initialize_sql('postgresql://postgres:postgres@localhost:5432/gateway')
    session = DBSession()
    circuit = session.query(Circuit).get(circuit_id)
    annotation.append('circuit_id = ' + str(circuit_id))
    annotation.append('meter name =' + circuit.meter.name)
    annotation.append('circuit ip =' + circuit.ip_address)
    annotation.append(dateStart.strftime('%Y-%m-%d') + ' to ' + dateEnd.strftime('%Y-%m-%d'))
    annotation = '\n'.join(annotation)

    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.autofmt_xdate()
    # if no titleString passed in, use default
    if titleString == None:
        titleString = 'circuit ' + str(circuit_id) + ' - ' + dateStart.strftime('%Y%m%d') + ' multiple'
    fig.suptitle(titleString)
    if introspect:
        plt.show()
    fig.savefig(titleString + '.pdf')
    plt.close()

def plotDataForCircuit(circuit_id,
                            dateStart=dt.datetime(2011,5,12),
                            dateEnd=dt.datetime(2011,5,13),
                            quantity='watthours',
                            introspect=False):
    dates, data = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity)
    dates = matplotlib.dates.date2num(dates)
    fig = plt.figure()
    ax = fig.add_axes((.2,.2,.6,.6))
    ax.grid(linestyle='-', color='#eeeeee')
    ax.plot_date(dates, data, 'ko-')
    titleString = 'circuit ' + str(circuit_id) + quantity
    #ax.set_title(titleString)
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Cumulative Energy Consumed (Wh)')
    #ax.set_xlim(matplotlib.dates.date2num(dt.datetime(2011,9,25)),
    #            matplotlib.dates.date2num(dt.datetime(2011,9,26)))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
    #from matplotlib.dates import HourLocator
    #ax.xaxis.set_major_locator(HourLocator(byhour=[0,6,12,18,24]))
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(titleString + '.pdf',transparent=True)

def plotPowerForCircuit(circuit_id,
                        dateStart=dateStart,
                        dateEnd=dateEnd,
                        introspect=False):
    dates, data, num_decreases = calculatePowerListForCircuit(circuit_id, dateStart, dateEnd)

    dates = matplotlib.dates.date2num(dates)
    fig = plt.figure()
    ax = fig.add_axes((.2,.2,.6,.6))
    ax.plot_date(dates, data, 'x-')
    titleString = 'circuit ' + str(circuit_id)
    ax.set_title(titleString)
    ax.set_ylabel("Power (W)")
    ax.set_xlabel("Time")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(titleString + '.pdf')


def plotDataForCircuitList(circuit_id_list,
                           dateStart=dateStart,
                           dateEnd=dateEnd,
                           quantity='credit',
                           introspect=False):
    '''
    this function takes a list of circuit ids and plots a grid of data for the
    specified quantity over the specified date range
    '''
    pass


'''
plot credit or watthours for all circuits on a meter
'''
def plotDataForAllCircuitsOnMeter(meter_id,
                              dateStart=dateStart,
                              dateEnd=dateEnd,
                              quantity='credit',
                              introspect=False,
                              showMains=False):

    dtSt = str.replace(str(dateStart), ' 00:00:00', '')
    dtEnd = str.replace(str(dateEnd), ' 00:00:00', '')

    circuits = getCircuitsForMeter(meter_id)

    # drop mains circuit
    if showMains == False:
        for c in circuits:
            if session.query(Circuit).filter(Circuit.id == c)[0].ip_address == '192.168.1.200':
                circuits.remove(c)


    fig = plt.figure()
    plt.subplots_adjust(wspace=0.5)

    # create figure and axes with subplots
    if len(circuits) > 12:
        numPlotsX = 4
        numPlotsY = 5
    else:
        numPlotsX = 4
        numPlotsY = 3

    # loop through circuits, get data, plot
    for i,c in enumerate(circuits):
        dates, data = getDataListForCircuit(c, dateStart, dateEnd, quantity)
        dates = matplotlib.dates.date2num(dates)

        thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1)
        thisAxes.plot_date(dates, data, ls='-', c='#eeeeee', ms=3, marker='o', mfc=None)
        thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
        thisAxes.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(minticks=3,maxticks=5))
        thisAxes.text(0.7,0.7,str(c),transform = thisAxes.transAxes)

    fileNameString = 'meter ' + quantity + ' ' + str(meter_id) + '-' + dtSt + 'to' + dtEnd + '.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(fileNameString)


#--------------------------------------------------------------------------------------------#
# printing functions

def printHugeMessageTable(dateStart=dateStart,
                          dateEnd=dateEnd):
    '''
    prints a table of whether or not circuits have reported on certain dates
    '''

    # get list of circuits
    circuit = session.query(Circuit).all()
    clist = [c.id for c in circuit]
    clist.sort()

    originalQuery = session.query(PrimaryLog)

    start = dateStart
    while 1:
        # set endpoint at end of hour
        end = start + dt.timedelta(hours=1)

        # make temp copy of query
        thisQuery = originalQuery

        # take reports in the hour between start and end
        thisQuery = thisQuery.filter(PrimaryLog.date >= start)
        thisQuery = thisQuery.filter(PrimaryLog.date < end)

        # create and sort list of reporting logs
        cclist = [tq.circuit_id for tq in thisQuery]
        cclist.sort()

        # output to screen starting with date and then circuit_id or hyphen
        print start,
        print "".join([str(x).ljust(3) if x in cclist else ' - ' for x in clist])

        # increment date and check for end condition
        start = start + dt.timedelta(hours=1)
        if start >= dateEnd:
            break

'''
prints a table of consumption and mean and stdev for a meter and daterange
'''
def printTableOfConsumption(meter_id,
                       dateStart=dt.datetime(2011,5,13),
                       dateEnd = dt.datetime(2011,5,17),
                       strict=True):
    dates, circuit_id, data = calculateTableOfConsumption(meter_id, dateStart, dateEnd, strict=strict)
    print ' '.ljust(10),
    for cid in circuit_id:
        print str(cid).rjust(6),
    print
    for i,date in enumerate(dates):
        print date.strftime("%Y-%m-%d").ljust(10),
        for d in data[i]:
            print str(d).rjust(6),
        print
    print 'mean'.ljust(10),
    for m in data.mean(0):
        print ('%0.2f' % m).rjust(6),
    print
    print 'stdev'.ljust(10),
    for m in data.std(0):
        print ('%0.2f' % m).rjust(6),
    print

# uncategorized functions

def removeDuplicates(dates, created, data):
    # remove midnight sample from the future
    # by creating a boolean mask and then indexing arrays based on that mask
    mask = []
    if len(dates)==0:
        return [],[]
    for i in range(len(dates)):
        if (created[i] - dates[i]).total_seconds() < 3600:
            mask.append(True)
        else:
            mask.append(False)
    mask = np.array(mask)
    dates = dates[mask]
    data = data[mask]

    # put data into tuples and run set to get unique samples
    dataList = []
    for i in range(len(dates)):
        dataList.append((dates[i], data[i]))
    dataList = list(set(dataList))
    dataList.sort()
    dates = [d[0] for d in dataList]
    data = [d[1] for d in dataList]
    return dates, data

def inspectDayOfWatthours(circuit_id,
                          day=dt.datetime(2011,5,28),
                          verbose=0):
    dates, created, data = getRawDataListForCircuit(circuit_id,
                                                    day,
                                                    day + dt.timedelta(days=1),
                                                    quantity='watthours')
    print 'number of raw samples = ', len(dates)
    dates, data = removeDuplicates(dates, created, data)
    print 'number of samples after duplicate removal = ', len(dates)

    data = np.array(data)
    power = np.diff(data)
    dates = np.array(dates)

    # mask values with decrease in watthours and adjust for by one offset
    # want to remove drops at midnight which are normal
    decreaseMask = power < 0

    np.insert(decreaseMask, 0, False)
    #should be last one per day? (unless there's a drop at 11pm and no report at 12.
    if len(decreaseMask)>0:
        if decreaseMask[-1] == 1:
            decreaseMask[-1] = False
    else: return []


    print 'decrease in watthours observed at these', sum(decreaseMask), 'times'
    print dates[decreaseMask]
    return dates[decreaseMask]
    print 'apparent power consumption for day using max = ', max(data)

    '''
    print power
    print dates
    print data
    '''

def plotDaysOfWatthourDrops(circuit_id,
                          dateStart=dt.datetime(2011,5,28), dateEnd=dt.datetime(2011,6,3),
                          verbose=0):

    dates = []
    # break up time period into days
    num_days = dateEnd - dateStart
    beg_day = dateStart
    for k in range(num_days.days):
        errortimes = inspectDayOfWatthours(circuit_id, beg_day)
        if len(errortimes)>0:
            #remove times from dates
            for i in range(len(errortimes)):
                #errordates = errortimes[i].strftime('%Y,%m,%d')
                errordates = dt.datetime(errortimes[i].year, errortimes[i].month, errortimes[i].day)
            dates = np.append(dates, errordates)
            beg_day = beg_day + dt.timedelta(days=1)
    #print dates
    dates = list(set(dates))
    dates.sort()
    print dates
    for d in range(len(dates)):
        plotDatasForCircuit(circuit_id, dates[d], dates[d] + dt.timedelta(days=1))

'''
for a given circuit_id and date range, this function returns a list of
data specified by quantity.  uses set() to remove duplicate entries.
also discards entries if the gateway time stamp is more than one hour
ahead of the meter time stamp
input:
    circuit_id - circuit database id
    dateStart - datetime object for day of data.  data returned dateStart < date <= dateEnd
    dateEnd - datetime object specifying end of data
    quantity - 'watthours' or 'credit'
    verbose - 1 gives an output to console of the data list
            - 0 no output
output:
    dates - list of date stamps corresponding to data list
    data - list of reported data
'''
def getDataListForCircuit(circuit_id,
                              dateStart=dateStart,
                              dateEnd=dateEnd,
                              quantity='watthours',
                              verbose=0):
    '''
    for a given circuit_id and date range, this function returns a list of
    data specified by quantity.  uses set() to remove duplicate entries.
    also discards entries if the gateway time stamp is more than one hour
    ahead of the meter time stamp
    input:
        circuit_id - circuit database id
        dateStart - datetime object for day of data.  data returned dateStart < date <= dateEnd
        dateEnd - datetime object specifying end of data
        quantity - 'watthours' or 'credit'
        verbose - 1 gives an output to logging of the data list
                - 0 no output
    output:
        dates - list of date stamps corresponding to data list
        data - list of reported data
    '''
    # get numpy arrays of dates, timestamps, and data
    tw.log.info('->->-> getDataListForCircuit')
    tw.log.info('       circuit  = ' + str(circuit_id))
    tw.log.info('       quantity = ' + quantity)
    dates, created, data = getRawDataListForCircuit(circuit_id,
                                                    dateStart,
                                                    dateEnd,
                                                    quantity,
                                                    verbose)

    # if data empty return two empty lists
    if len(dates) == 0:
        tw.log.info('returning empty lists')
        #print 'no data for circuit', circuit_id, 'between', dateStart, 'and', dateEnd
        return [],[]

    # remove midnight sample from the future
    # by creating a boolean mask and then indexing arrays based on that mask
    mask = []
    for i in range(len(dates)):
        if (created[i] - dates[i]).total_seconds() < 3600:
            mask.append(True)
        else:
            mask.append(False)
            #tw.log.info('removing sample at ' + str(dates[i]) + ' from the future')


    '''
    mask = np.array(mask)
    tw.log.info('removing ' + str(len(np.extract(mask==False,mask))) + ' samples from the future')

    dates = dates[mask]
    data = data[mask]
    '''
    # put data into tuples and run set to get unique samples
    dataList = []
    for i in range(len(dates)):
        dataList.append((dates[i], data[i]))
    num_raw_samples = len(dataList)
    tw.log.info('number of raw samples    = ' + str(num_raw_samples))
    dataList = list(set(dataList))
    num_unique_samples = len(dataList)
    tw.log.info('number of unique samples = ' + str(num_unique_samples))
    dataList.sort()
    dates = [d[0] for d in dataList]
    data = [d[1] for d in dataList]

    if verbose > 0:
        for d in dataList:
            tw.log.info(str(d))
    tw.log.info('<-<-<- getDataListForCircuit')
    return dates, data

def getRawDataListForCircuit(circuit_id,
                              dateStart=dt.datetime(2011,5,28),
                              dateEnd=dt.datetime(2011,5,29),
                              quantity='watthours',
                              verbose=0):
    # get query based on circuit and date
    # and sort by date received by gateway
    initialize_sql('postgresql://postgres:postgres@localhost:5432/gateway')
    session = DBSession()
    logs = session.query(PrimaryLog)\
                  .filter(PrimaryLog.circuit_id == circuit_id)\
                  .filter(PrimaryLog.date > dateStart)\
                  .filter(PrimaryLog.date <= dateEnd)\
                  .order_by(PrimaryLog.date)

    # create separate arrays for each of these quantities
    dates = np.array([l.date for l in logs])
    data  = np.array([getattr(l, quantity) for l in logs])
    created = np.array([l.created for l in logs])

    return dates, created, data


def calculatePowerListForCircuit(circuit_id,
                                       dateStart=dateStart,
                                       dateEnd=dateEnd):
    '''
    pulls watthour data list and creates a report of the power consumed over that hour
    returns numpy arrays of power_dates, and power_data
    '''
    tw.log.info('running calculatePowerListForCircuit on ' + str(circuit_id))
    dates, data = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity='watthours')

    power_dates = []
    power_data = []
    num_decreases = 0
    # if data empty return two empty lists
    if len(dates) == 0:
        tw.log.info('returning empty lists')
        #print 'no data for circuit', circuit_id, 'between', dateStart, 'and', dateEnd
        return [],[]
    for i in range(len(dates)):
        # if 1am energy sample is energy over last hour
        if dates[i].hour == 1:
            power_dates.append(dates[i])
            power_data.append(data[i])
        # only append if not 1am, after the first sample and if power is positive
        if (dates[i].hour != 1) and (i > 0) and ((dates[i] - dates[i-1]) == dt.timedelta(hours=1)):
            if (data[i] - data[i-1]) >= 0:
                power_dates.append(dates[i])
                power_data.append(data[i] - data[i-1])
            else: num_decreases += 1

    power_dates = np.array(power_dates)
    power_data = np.array(power_data)

    return power_dates, power_data, num_decreases

def printEnergyGridForCircuits(circuit_id_list,
                        dateStart = dateStart,
                        dateEnd = dateEnd):

    printTableRow(("circuit", "max", "mean", "min"),(4,20,20,20))

    for i,c in enumerate(circuit_id_list):
        # grab energy data for circuit
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        printTableRow((c,max(data),data.mean(),data.min()),(4,20,20,20))
        '''
        print c,
        print max(data),
        print data.mean(),
        print data.min()
        '''

def plotEnergyGridForCircuits(circuit_id_list,
                        dateStart = dateStart,
                        dateEnd = dateEnd):

    fig = plt.figure()
    # create figure and axes with subplots
    if len(circuit_id_list) > 12:
        numPlotsX = 4
        numPlotsY = 5
    else:
        numPlotsX = 4
        numPlotsY = 3
    #fig, axes = plt.subplots(numPlotsY, numPlotsX, sharex=True)

    plt.subplots_adjust(wspace=0.5)

    # loop through circuits, get data, plot
    for i,c in enumerate(circuit_id_list):
        # grab energy data for circuit
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        print c, max(data), data.mean(), data.min()
        dates = matplotlib.dates.date2num(dates)

        thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1)
        #thisAxes = axes[i/numPlotsY, i%numPlotsX]
        thisAxes.plot_date(dates, data, ls='-', ms=3, marker='o', mfc=None)
        thisAxes.set_ylim((0,50))
        #thisAxes.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=(0)))
        thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
        thisAxes.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(minticks=3,maxticks=5))
        thisAxes.text(0.5,0.7,str(c),transform = thisAxes.transAxes)

    fileNameString = 'testenergyplotgrid.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    #if introspect:
    #    plt.show()
    fig.savefig(fileNameString)

def getAveragedPowerForCircuit(circuit_id, dateStart=dateStart,
                               dateEnd = dateEnd):
    '''
    returns a numpy array of power for hour of day
    '''
    # get list for entire date range
    dates, data = calculatePowerListForCircuit(circuit_id, dateStart=dateStart, dateEnd=dateEnd)

    # create dictionary with key = hour and value = []
    dataDict = {}
    for hour in range(0,24):
        dataDict[hour] = []

    # iterate over list and place samples in a dictionary with key=hour
    for i, date in enumerate(dates):
        dataDict[date.hour].append(data[i])

    avg_power = []
    for key in dataDict.keys():
        avg_power_for_hour = np.array(dataDict[key]).mean()
        avg_power.append(avg_power_for_hour)

    return np.array(avg_power)



def plotAveragedPowerForCircuit(circuit_id,
                                dateStart=dateStart,
                                dateEnd=dateEnd,
                                plotFileName='averagePower.pdf'):
    # get list for entire date range
    dates, data = calculatePowerListForCircuit(circuit_id, dateStart=dateStart, dateEnd=dateEnd)

    # create dictionary with key = hour and value = []
    dataDict = {}
    for hour in range(0,24):
        dataDict[hour] = []

    # iterate over list and place samples in a dictionary with key=hour
    for i, date in enumerate(dates):
        dataDict[date.hour].append(data[i])

    # iterate over keys and average watthour readings for each hour

    # plot both of these

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.3, 0.8, 0.6))
    for key in dataDict.keys():
        # construct a list of hours the same length as dictionary list
        hour = key * np.ones(len(dataDict[key]))
        #ax.plot(hour, dataDict[key],',', mfc='#dddddd', mec='#dddddd')
        avg_energy_for_hour = np.array(dataDict[key]).mean()
        #ax.plot(key, avg_energy_for_hour, 's', ms=10)
        yerr = np.std(dataDict[key])
        ax.errorbar(key, avg_energy_for_hour, yerr=yerr, marker='s',
         mfc='0.85', mec='black', ms=6, mew=1, fmt='-', ecolor='k')

    ax.axis([-1,24,0,10])
    '''
    # tick labels with fontprops
    plt.setp(ax.get_xticklabels(), fontproperties=tickFont)
    plt.setp(ax.get_yticklabels(), fontproperties=tickFont)
    '''

    '''     MEAN almost always 0...
    bp = plt.boxplot(dataDict, notch=0, sym='+', vert=1, whis=1.5)
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='gray', marker='+')
    '''
    ax.set_xlabel('Hour of Day')    #, fontproperties=labelFont)
    ax.set_ylabel('Average Power (Watts)')  #, fontproperties=labelFont)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotAveragedPowerForCircuit.__name__)
    annotation.append('circuit = ' + str(circuit_id))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)

    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(plotFileName, transparent=True)

def plotAveragedAccumulatedHourlyEnergyForCircuit(circuit_id,
                                                  dateStart=dateStart,
                                                  dateEnd=dateEnd,
                                                  plotFileName = 'averagedAccumulatedEnergy.pdf'):
    '''
    plots averaged consumption for a single circuit
    report on the hour reports consumption for previous hour
    '''

    # get list for entire date range
    dates, data = getDataListForCircuit(circuit_id, dateStart=dateStart, dateEnd=dateEnd)

    # create dictionary with key = hour and value = []
    dataDict = {}
    for hour in range(0,24):
        dataDict[hour] = []

    # iterate over list and place samples in a dictionary with key=hour
    for i, date in enumerate(dates):
        dataDict[date.hour].append(data[i])

    # iterate over keys and average watthour readings for each hour

    # plot both of these

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.1, 0.8, 0.8))
    for key in dataDict.keys():
        # construct a list of hours the same length as dictionary list
        hour = key * np.ones(len(dataDict[key]))
        ax.plot(hour, dataDict[key],'o', mfc='#dddddd', mec='#dddddd')
        avg_energy_for_hour = np.array(dataDict[key]).mean()
        ax.plot(key, avg_energy_for_hour, 'kx', ms=10)
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Acumulated Energy (Watthours)')
    fig.savefig(plotFileName)


def plot_power_histogram_circuit(circuit_id,
                         dateStart=dateStart,
                         dateEnd=dateEnd,
                         bins=None,
                         plotFileName=None):
    dataList = np.array([])
    data, dates, num_decreases = calculatePowerListForCircuit(circuit_id, dateStart, dateEnd)
    dataList = np.append(dataList, data)

    # prune out zero wattage readings
    dataList = dataList[dataList > 0]

    fig = plt.figure()
    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    ax.hist(dataList, bins=bins, normed=False, facecolor='#dddddd')
    if plotFileName == None:
        plotFileName = 'power_histogram_' + str(circuit_id) + '.pdf'
    fig.savefig(plotFileName, transparent=True)

def plot_power_histogram(circuit_id_list,
                         dateStart=dateStart,
                         dateEnd=dateEnd,
                         bins=None,
                         plotFileName=None):

    dataList = np.array([])
    for i,c in enumerate(circuit_id_list):
        data, dates, num_decreases = calculatePowerListForCircuit(c, dateStart, dateEnd)
        tw.log.info('number of energy readings = ' + str(len(data)))
        # append data onto master list of energy
        dataList = np.append(dataList, data)
        tw.log.info('len dataList = ' + str(len(dataList)))

    dataList = dataList[dataList > 0]

    fig = plt.figure()
    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    # range depends on data
    '''
    if bins == None:
        high = int(np.ceil(max(dataList)) + 5)
        #bins = [0,1] + range(5,high,5)
        bins = range(0, high, 5)
    '''
    ax.hist(dataList, bins=bins, normed=False, facecolor='#dddddd')
    '''
    ax.set_xlabel("Daily Watthours")    #, fontproperties=labelFont)
    ax.set_ylabel("Days of Usage")  #, fontproperties=labelFont)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotEnergyHistogram.__name__)
    annotation.append('circuits = ' + str(circuit_id_list))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    for ann in annotation:
        tw.log.info(ann)
    annotation = '\n'.join(annotation)
    '''
    #plt.show()
    #fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    if plotFileName == None:
        plotFileName = 'power_histogram_multiple.pdf'
    fig.savefig(plotFileName, transparent=True)

def plotEnergyHistogram(circuit_id_list,
                        dateStart=dateStart,
                        dateEnd=dateEnd,
                        bins=None,
                        plotFileName='energyHistogram.pdf'):
    tw.log.info('entering plotEnergyHistogram')

    dataList = np.array([])
    for i,c in enumerate(circuit_id_list):
        # grab energy data for circuit
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        tw.log.info('number of energy readings = ' + str(len(data)))
        # append data onto master list of energy
        dataList = np.append(dataList, data)
        tw.log.info('len dataList = ' + str(len(dataList)))
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    # range depends on data
    if bins == None:
        high = int(np.ceil(max(dataList)) + 5)
        #bins = [0,1] + range(5,high,5)
        bins = range(0, high, 5)
    ax.hist(dataList, bins=bins, normed=False, facecolor='#dddddd')
    ax.set_xlabel("Daily Watthours")    #, fontproperties=labelFont)
    ax.set_ylabel("Days of Usage")  #, fontproperties=labelFont)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotEnergyHistogram.__name__)
    annotation.append('circuits = ' + str(circuit_id_list))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    for ann in annotation:
        tw.log.info(ann)
    annotation = '\n'.join(annotation)

    #plt.show()
    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(plotFileName, transparent=True)

def getEnergyForCircuitForDayByMax(circuit_id,
                                   day=dt.datetime(2011,6,8)):
    '''
    needs to check for sufficient number of data samples
    needs to check for watthour drops
    '''
    tw.log.info('->->-> getEnergyForCircuitForDayByMax')
    tw.log.info('       circuit = ' + str(circuit_id))
    tw.log.info('          date = ' + str(day))
    dates, watthours = getDataListForCircuit(circuit_id,
                                             day,
                                             day+dt.timedelta(days=1),
                                             quantity='watthours')
    if len(watthours) > 0:
        energy = max(watthours)
    else:
        tw.log.info('no data')
        energy = 0
    power = np.diff(watthours)
    num_decreases = len(np.extract(power < 0, power))
    tw.log.info('samples of watthour data = ' + str(len(watthours)))
    if len(watthours) > 24:
        tw.log.error('too many watthour samples for one day')
    tw.log.info('number of watthour drops = ' + str(num_decreases))
    tw.log.info('reporting ' + str(energy) + ' watthours')
    tw.log.info('<-<-<- getEnergyForCircuitForDayByMax')
    return energy, len(watthours), num_decreases

def calculateAverageEnergyForCircuit(circuit_id=70,
                                     dateStart=dt.datetime(2011,6,1),
                                     dateEnd=dt.datetime(2011,7,7),
                                     verbose=0,
                                     num_drop_threshold=1,
                                     num_samples_threshold=18):
    '''
    calculates average energy for circuit over daterange
    rejecting samples with watthour drops and too few samples as specified
    by num_drop_threshold and num_samples_threshold
    '''
    data = []
    dates = []
    currentDate = dateStart
    average_energy = 0
    rejected_samples = 0
    average_energy_samples = 0
    while currentDate < dateEnd:
        energy, num_samples, num_drops = getEnergyForCircuitForDayByMax(circuit_id, currentDate)
        if verbose > 1:
            print currentDate,
            print energy, num_samples, num_drops
        if num_drops <= num_drop_threshold and num_samples >= num_samples_threshold:
            average_energy += energy
            average_energy_samples += 1
        else:
            rejected_samples += 1
        currentDate += dt.timedelta(days=1)
    if average_energy_samples > 0:
        average_energy /= average_energy_samples
    else:
        average_energy = 0

    if verbose > 0:
        print 'circuit =', circuit_id
        print 'average energy =', average_energy
        print 'number of samples =', average_energy_samples
        print 'rejected samples =', rejected_samples
    return average_energy

def getEnergyForCircuit(circuit_id,
                        dateStart=dateStart,
                        dateEnd=dateEnd):
    '''
    gets energy for circuit over date range specified by dateStart and dateEnd
    if no data, does not append to list
    '''
    tw.log.info('->->-> getEnergyForCircuit')
    data = []
    dates = []
    currentDate = dateStart
    while currentDate < dateEnd:
        result = getEnergyForCircuitForDayByMax(circuit_id, currentDate)
        if result[1] >= 24 and result[0] != 0.0:
            data.append(result[0])
            dates.append(currentDate)
        else:
            tw.log.info('rejected data for ' + str(currentDate))
        currentDate += dt.timedelta(days=1)
    data = np.array(data)
    tw.log.info('<-<-<- getEnergyForCircuit')
    return data, dates

def energyTest(circuit_id_list, dateStart=dt.datetime(2011,6,5),
                           dateEnd=dt.datetime(2011,6,8)):

    for circuit_id in circuit_id_list:
        date = dateStart
        while date < dateEnd:
            print date.strftime('%Y-%m-%d'), circuit_id, getEnergyForCircuitForDayByMax(circuit_id, date)
            date += dt.timedelta(days=1)

'''
for a meter and daterange, outputs a table of percentage of time that greater
than zero credit is in the account.
'''
def calculateTimeWithCredit(meter_id,
                            dateStart=dt.datetime(2011,4,1),
                            dateEnd = dt.datetime(2011,5,1)):
    circuit_id = getCircuitsForMeter(meter_id)

def calculateTimeWithCreditForCircuit(circuit_id,
                                      dateStart=dateStart,
                                      dateEnd=dateEnd):
    dates, credit = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity='credit')
    credit = np.array(credit)
    hoursWithCredit = len(np.extract(credit > 0, credit))
    totalHours = len(credit)
    timeWithCredit = float(hoursWithCredit) / float(totalHours)
    return timeWithCredit

def calculateTimeWithCreditForCircuitList(circuit_id_list,
                                          dateStart=dateStart,
                                          dateEnd=dateEnd):
    '''
    for a meter and daterange, outputs a table of percentage of time that greater
    than zero credit is in the account.
    '''
    print ' '.ljust(10),
    for cid in circuit_id_list:
        print str(cid).rjust(6),
    print
    print '% credit'.ljust(10),
    credit_list = []
    for cid in circuit_id_list:
        timeWithCredit = calculateTimeWithCreditForCircuit(cid, dateStart, dateEnd)
        credit_list.append(timeWithCredit)
        print ('%0.2f' % timeWithCredit).rjust(6),
    print
    return credit_list

def plotScatterCreditConsumedVsTimeWithCreditForCircuitList(circuit_id_list,
                                                            dateStart=dateStart,
                                                            dateEnd=dateEnd,
                                                            plotFileName='scatterCreditTime.pdf'):
    credit_consumed = printReportOfCreditConsumedForCircuitList(circuit_id_list, dateStart, dateEnd)
    # convert to USD
    credit_consumed = [x*toUSD for x in credit_consumed]
    time_with_credit = calculateTimeWithCreditForCircuitList(circuit_id_list, dateStart, dateEnd)
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    ax.plot(credit_consumed, time_with_credit, 'o', mfc='#cccccc')
    '''
    # ticklabels with fontprops---------------
    plt.setp(ax.get_xticklabels(), fontproperties=tickFont)
    plt.setp(ax.get_yticklabels(), fontproperties=tickFont)
    '''
    ax.set_xlim((0,5))
    ax.set_xlabel('Monthly Electricity Expenditure (USD)')  #, fontproperties=labelFont)
    ax.set_ylabel('Fraction of Time with Credit Available') #, fontproperties=labelFont)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotScatterCreditConsumedVsTimeWithCreditForCircuitList.__name__)
    annotation.append('circuits = ' + str(circuit_id_list))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)

    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(plotFileName, transparent=True)


def calculateAverageTimeWithCreditForCircuitList(circuit_id_list,
                                                 dateStart=dateStart,
                                                 dateEnd=dateEnd):
    averageTime = 0
    numCircuits = len(circuit_id_list)
    for cid in circuit_id_list:
        timeWithCredit = calculateTimeWithCreditForCircuit(cid, dateStart, dateEnd)
        averageTime += timeWithCredit / numCircuits
    return averageTime

def plotHistogramTimeWithCreditForCircuitList(circuit_id_list,
                                              dateStart=dateStart,
                                              dateEnd=dateEnd,
                                              rg=(0.0, 1.0),
                                              plotFileName='timeWithCreditHistogram.pdf'):
    timeList = []
    for cid in circuit_id_list:
        timeWithCredit = calculateTimeWithCreditForCircuit(cid, dateStart, dateEnd)
        timeList.append(timeWithCredit)

    # plot histogram
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    hist, bin_edges = np.histogram(timeList, bins=10, range=rg)
    ax.bar(bin_edges[:-1], hist, width=0.1, color='#dddddd')
    ax.set_xlabel("Percentage of time with credit available")   #, fontproperties=labelFont)
    ax.set_ylabel("Customers")  #, fontproperties=labelFont)
    ax.set_xlim(rg)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotHistogramTimeWithCreditForCircuitList.__name__)
    annotation.append('circuits = ' + str(circuit_id_list))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)

    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(plotFileName, transparent=True)

def plotHistogramCreditConsumed(circuit_id_list,
                                dateStart=dateStart,
                                dateEnd=dateEnd,
                                bins=None,
                                plotFileName='consumptionHistogram.pdf'):

    consumptionList = printReportOfCreditConsumedForCircuitList(circuit_id_list, dateStart, dateEnd)
    # convert to USD
    consumptionList = [x*toUSD for x in consumptionList]

    if bins==None:
        high = np.ceil(max(consumptionList)) + 0.5
        bins = np.arange(0, high, 0.5)
    fig = plt.figure()

    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    ax.hist(consumptionList, bins=bins, normed=False, cumulative=False, facecolor='#dddddd')
    #ax.hist(consumptionList)
    ax.set_xlabel("Monthly Credit Consumed (USD)")  #, fontproperties=labelFont)
    ax.set_ylabel("Customers")  #, fontproperties=labelFont)

    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotHistogramCreditConsumed.__name__)
    annotation.append('circuits = ' + str(circuit_id_list))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)

    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(plotFileName, transparent=True)

def calculateCreditConsumedForCircuit(circuit_id,
                            dateStart=dateStart,
                            dateEnd=dateEnd,
                            threshold = 100,
                            verbose=0):
    dates, data = getDataListForCircuit(circuit_id,
                            dateStart=dateStart,
                            dateEnd=dateEnd,
                            quantity='credit')
    credit_derivative = np.diff(data)
    # only calculate decreases
    credit_derivative = np.extract(credit_derivative < 0, credit_derivative)
    # invert credit derivative
    credit_derivative *= -1
    # ignore decreases greater than threshold
    credit_derivative = np.extract(credit_derivative < threshold, credit_derivative)
    credit_consumed = sum(credit_derivative)
    return credit_consumed

def printReportOfCreditConsumedForCircuitList(circuit_id_list,
                            dateStart=dateStart,
                            dateEnd=dateEnd,
                            threshold = 100,
                            verbose=0):
    list = []
    for cid in circuit_id_list:
         list.append(calculateCreditConsumedForCircuit(cid, dateStart, dateEnd, threshold=500))
    print list
    return list

def calculateCreditJumps(circuit_id,
                            dateStart=dt.datetime(2011,5,13),
                            dateEnd=dt.datetime(2011,6,13),
                            verbose=0):
    #lowThreshold = 400

    dates, data = getDataListForCircuit(circuit_id,
                            dateStart,
                            dateEnd,
                            quantity='credit')
    dates = np.array(dates)
    data = np.array(data)
    diff = np.diff(data)
    mask = diff > 10
    np.delete(dates,0)
    #print diff[mask]
    #print dates[mask]

    if verbose > 0:
        for t in zip(diff[mask],dates[mask]):
            print circuit_id, str(t[0]).rjust(8), str(t[1]).rjust(21)

        print diff[mask].sum()
    #return diff[mask].sum()
    daysOfCredit = dates[mask], diff[mask]
    return daysOfCredit

def calculateCreditPurchase(circuit_id,
                            dateStart=dt.datetime(2011,5,13),
                            dateEnd=dt.datetime(2011,6,13),
                            verbose=0):
    addCredit = session.query(AddCredit)\
                       .filter(Job.circuit_id == circuit_id)\
                       .filter(Job.start >= dateStart)\
                       .filter(Job.start <= dateEnd)\
                       .order_by(Job.start)

    sum = 0
    creditList = []
    dateList = []

    for ac in addCredit:
            sum += ac.credit
            creditList = np.append(creditList, ac.credit)
            dateList = np.append(dateList, ac.start)
            if verbose > 0:
                print ac.id, ac.credit, ac.circuit_id, ac.start

    #return sum
    daysOfCredit = [dateList, creditList]
    return daysOfCredit

def plotCreditDiffs(meter_id, dateStart=dt.datetime(2011,5,13),
                        dateEnd=dt.datetime(2011,5,20),
                            verbose = 0, introspect=False, showMains=False):

    circuits = getCircuitsForMeter(meter_id)
    dtSt = str.replace(str(dateStart), ' 00:00:00', '')
    dtEnd = str.replace(str(dateEnd), ' 00:00:00', '')

    #get date labels
    num_days = dateEnd - dateStart
    dateList = []
    d = dateStart
    while d <= dateEnd:
        dateList.append(d)
        d += dt.timedelta(days=1)
    #print dateList
    yLabels = np.arange(0,1100,200)

    # drop mains circuit
    if showMains == False:
        for c in circuits:
            if session.query(Circuit).filter(Circuit.id == c)[0].ip_address == '192.168.1.200':
                circuits.remove(c)

    fig = plt.figure()

    # create figure and axes with subplots
    if len(circuits) > 12:
        numPlotsX = 4
        numPlotsY = 5
    else:
        numPlotsX = 4
        numPlotsY = 3

    for i,c in enumerate(circuits):
        calculatedCredits = calculateCreditJumps(c, dateStart, dateEnd, verbose)
        loggedPurchases = calculateCreditPurchase(c, dateStart, dateEnd, verbose)

        dates = np.union1d(calculatedCredits[0], loggedPurchases[0])
        print dates
        dates = matplotlib.dates.date2num(dates)
        print dates
        #dates = list(set(dates))
        #dates.sort()
        calculatedCreditDates = matplotlib.dates.date2num(calculatedCredits[0])
        mask1 = []
        for l in range(len(calculatedCreditDates)):
            ind = np.where(dates==calculatedCreditDates[l])
            #print ind
            mask1.append(int(ind[0]))       #because ind was an array of arrays!
        print mask1
        #mask1 = np.where(dates,calculatedCredits[0])
        #mask1 = np.setmember1d(dates, calculatedCredits[0])    #mergesort not avail for type
        data1 = [-100]*len(dates)
        for k in range(len(mask1)):
            data1[mask1[k]] = calculatedCredits[1][k]
        #data1[np.invert(mask1)] = 0
        print data1
        #mask2 = np.in1d(dates,loggedPurchases[0])
        #mask2 = dates == loggedPurchases[0]
        #mask2 = np.setmember1d(dates, loggedPurchases[0])  #mergesort not avail for type
        purchaseDates = matplotlib.dates.date2num(loggedPurchases[0])
        mask2 = []
        for l in range(len(purchaseDates)):
            ind = np.where(dates==purchaseDates[l])
            #print ind
            mask2.append(int(ind[0]))
        data2 = [-100]*len(dates)
        for j in range(len(mask2)):
            data2[mask2[j]] = loggedPurchases[1][j]
        #data2[mask2] = loggedPurchases[1]
        #data2[np.invert(mask2)] = 0
        print data2
        '''
        dates, data = getDataListForCircuit(c, dateStart,dateEnd,quantity='credit')
        dates = matplotlib.dates.date2num(dates)
        data1 = calculatedCredits[1]
        data2 = loggedPurchases[1]
        '''
        # how to make xlabels & ylabels smaller?
        # how to make room for xlabels on all graphs?
        thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1, xlim=(dateStart, dateEnd), ylim=(0,1100)) #to keep all plots even, assuming 1100 is enough
        thisAxes.plot_date(dates, data1, ls=' ', ms=7, marker='o', c='b')
        thisAxes.plot_date(dates, data2, ls=' ', ms=12, marker='x', c='r')
        thisAxes.set_xticklabels(dateList)  #, fontproperties=textFont)
        thisAxes.set_yticklabels(yLabels)   #, fontproperties=textFont)
        #thisAxes.xlim(xmin=1)
        thisAxes.text(0.7,0.7,str(c),size="x-small", transform = thisAxes.transAxes)


    fileNameString = 'credit diffs on meter ' +  ' ' + str(meter_id) + '-' + dtSt + 'to' + dtEnd + '.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(fileNameString)

def printCreditPurchase(cid_list,
                       dateStart=dt.datetime(2011,6,1),
                       dateEnd=dt.datetime(2011,6,13)):
    for i, cid in enumerate(cid_list):
        sum = calculateCreditPurchase(cid, dateStart, dateEnd)
        print cid, sum


if __name__ == "__main__":
    pass
    plotDataForCircuit(134, dateStart=dt.datetime(2011,9,25),
                            dateEnd=dt.datetime(2011,9,26), introspect=False)

