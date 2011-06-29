from sql.analysis import *

import datetime as dt

#font properties---------------------
import matplotlib.font_manager as mpf
#for labels
labelFont = mpf.FontProperties()
labelFont.set_family('serif')
labelFont.set_size(14)
#labelFont.set_linespacing(1.5)
#font prop's for annotation
textFont = mpf.FontProperties()
textFont.set_family('monospace')
textFont.set_size(6)

def writeMessageRateOfMeters(dateStart=dt.datetime(2011,6,24), dateEnd=today, fullWrite=True):
    '''
    if difference(circuit_id_list.sort, mali001) == 0:
        meter = mali001
    elif difference(circuit_id_list.sort, ml05) == 0:
        meter = ml05
    elif difference(circuit_id_list.sort, ml06) == 0:
        meter = ml06
    elif difference(circuit_id_list.sort, uganda002) == 0:
        meter = uganda002
    else print 'your circuit list does not match known meters'
    filename = 'msgs/' + meter + '_messagerate.csv'
    '''
    filename = 'message_received_rate.txt'
    meters = [4,6,7,8]
    import os
    if os.path.isfile(filename) and fullWrite == False:
        t = os.path.getmtime(filename)
        lastDate = dt.datetime.fromtimestamp(t) #.date()
        f = open(filename, 'a')
        currentDate = lastDate + dt.timedelta(days=1)
        while currentDate < dateEnd:
            for m in range(len(meters)):
                mrate=[]
                avg_mrate =[]
                circuit_id_list = getCircuitsForMeter(meters[m])
                f.append(str(currentDate));f.write('\t')
                f.write(str(meters[m]));f.write('\t')
                for i,c in enumerate(circuit_id_list):
                    dates, data = getDataListForCircuit(c, currentDate, currentDate+dt.timedelta(days=1))
                    mrate.append(len(dates)/24.0)
                    avg_mrate.append(sum(mrate)/len(mrate))
                f.write(str(sum(avg_mrate)/len(avg_mrate)));f.write('\n')
            currentDate += dt.timedelta(days=1)
    else:
        f = open(filename, 'w')
        currentDate = dateStart
        while currentDate < dateEnd:
            for m in range(len(meters)):
                mrate=[]
                circuit_id_list = getCircuitsForMeter(meters[m])
                avg_mrate=[]
                f.write(str(currentDate));f.write('\t')
                f.write(str(meters[m]));f.write('\t')
                for i,c in enumerate(circuit_id_list):
                    #mrate = []
                    dates, data = getDataListForCircuit(c, currentDate, currentDate+dt.timedelta(days=1))
                    mrate.append(len(dates)/24.0)
                    avg_mrate.append(sum(mrate)/len(mrate))
                f.write(str(sum(avg_mrate)/len(avg_mrate)));f.write('\n')
            currentDate += dt.timedelta(days=1)
    f.close()

def plotMessageRateOfMeters(dateStart=dt.datetime(2011,6,24), dateEnd=today):
    meters = [4,6,7,8]
    currentDate=dateStart
    dateList = []
    d = dateStart
    while d < dateEnd:  #-dt.timedelta(days=1):
        dateList.append(d)
        d += dt.timedelta(days=1)
    mrate=[[]*len(meters) for x in xrange(len(meters))]
    while currentDate < dateEnd:
        for m in range(len(meters)):
            cct_mrate =[]
            circuit_id_list = getCircuitsForMeter(meters[m])
            #avg_mrate=[]
            for i,c in enumerate(circuit_id_list):
                dates, data = getDataListForCircuit(c, currentDate, currentDate+dt.timedelta(days=1))
                cct_mrate.append(len(dates)/24.0)
            mrate[m].append(sum(cct_mrate)/len(cct_mrate))
        currentDate += dt.timedelta(days=1)
    print mrate
    fig = plt.figure()
    ax = fig.add_axes((.1,.3,.8,.6))
    for m in range(len(meters)):
        ax.plot(dateList, mrate[m], 'x-', label=getMeterName(meters[m]))
        #ax.legend(getMeterName(meters[m]), loc=(0.9,0.9-(0.1*m)))
        #fig.text(0.85,(0.01+0.05*m),getMeterName(meters[m]))
    ax.legend(loc=0)
    #fig.legend()
    titleString = 'meters-messages received ' + dateStart.date().__str__() + '_to_' + dateEnd.date().__str__()
    ax.set_title(titleString)
    ax.set_ylabel("% messages received")
    ax.set_xlabel("Date")
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotMessageRateOfMeters.__name__)
    annotation.append('meters = ' + str(meters))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)
    #plt.show()
    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    plotFileName = titleString + '.pdf'
    fig.savefig(plotFileName, transparent=True)

#plotMessageRateOfMeters()

def printEnergyUsedPerDayByCircuitsOnMeter(circuit_id_list, dateStart=dateStart, dateEnd=dateEnd):
    dataList = np.array([])
    for i,c in enumerate(circuit_id_list):
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        dataList = np.append(dataList, data)
        print c, dates[0].date(), data[0]

def getMeterName(mid):
    name = session.query(Meter).get(mid).name
    return name

def writeEnergyUsedPerDayByCircuitsOnMeter(meter=8, dateStart = dt.datetime(2011,6,24), dateEnd=dt.datetime(2011,6,27)):

    metername = getMeterName(meter)
    filename = 'sql/' + metername + '_daily_energy.txt'
    f = open(filename, 'w')

    circuit_id_list = getCircuitsForMeter(meter)
    header = ['date']
    for m in range(len(circuit_id_list)):
        #print meter[m]
        header.append(str(circuit_id_list[m]))
    #mstring = [str(m) for m in meter]
    #print mstring
    #header = ['date', [mstring[y] for y in range(len(mstring))]]
    print header
    for i in range(len(header)):
        f.write(header[i])
        f.write('\t')
    f.write('\n')
    currentDate = dateStart
    while currentDate < dateEnd:
        #stringline = [str(currentDate)]
        f.write(str(currentDate))
        f.write('\t')
        for i,c in enumerate(circuit_id_list):
            data, dates = getEnergyForCircuit(c, currentDate, currentDate+dt.timedelta(days=1))
            #stringline.append(str(data[0]))
            f.write(str(data[0]))
            f.write('\t')
        currentDate += dt.timedelta(days=1)
        f.write('\n')
    f.close()

#writeEnergyUsedPerDayByCircuitsOnMeter()

def specificTimeIssues(circuit_id_list=[81,82,84,89,90], dateStart=dt.datetime(2011,6,22), dateEnd = dateStart+dt.timedelta(days=1)):

    filename = 'sql/' + str(circuit_id_list) + 'etc_issues.txt'
    f = open(filename, 'w')
    header = ['date', 'created', 'watthours', 'credit', 'billing']
    '''
    for m in range(len(circuit_id_list)):
        header.append(str(circuit_id_list[m]))
        '''
    for i in range(len(header)):
        f.write(header[i])
        f.write('\t')
    f.write('\n')

    currentDate = dateStart
    while currentDate <dateEnd:
        f.write(str(currentDate))
        f.write('\t')
        for i, c in enumerate(circuit_id_list):
            dates,created,data=getRawDataListForCircuit(c,currentDate,currentDate+dt.timedelta(days=1),quantity='watthours')
            c_dates,c_created,c_data=getRawDataListForCircuit(c,currentDate, currentDate+dt.timedelta(days=1),quantity='credit')
            loggedPurchases=calculateCreditPurchase(c,currentDate, currentDate+dt.timedelta(days=1))
            l = len(loggedPurchases[0])
            for k in range(len(dates)):
                f.write(str(c));f.write('\t')
                f.write(str(dates[k]));f.write('\t')
                f.write(str(created[k]));f.write('\t')
                f.write(str(data[k]));f.write('\t')
                f.write(str(c_data[k]));f.write('\t')
                if k <= l:
                    f.write(str(loggedPurchases[k]))
                f.write('\n')
        currentDate += dt.timedelta(days=1)
    f.close()


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
        #from matplotlib import font_manager
        #smallsize = font_manager.FontProperties(size=mpl.rcParams['font.size'])
        thisAxes.set_xticklabels(dateList, fontproperties=textFont)
        thisAxes.set_yticklabels(yLabels, fontproperties=textFont)
        #thisAxes.xlim(xmin=1)
        thisAxes.text(0.7,0.7,str(c),size="x-small", transform = thisAxes.transAxes)


    fileNameString = 'credit diffs on meter ' +  ' ' + str(meter_id) + '-' + dtSt + 'to' + dtEnd + '.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(fileNameString)


def plotCctsWithWatthourDrops(meters=[4,6,7,8], dateStart=dt.datetime(2011,6,24), dateEnd=dt.datetime(2011,6,28),
                          verbose=0):

    #meters = [4,6,7,8]
    circuit_id_list=[]
    for m in range(len(meters)):
        ccts = getCircuitsForMeter(meters[m])
        #print ccts
        for x in range(len(ccts)):
            circuit_id_list.append(ccts[x])
    print circuit_id_list
    cctdates = [[]*len(circuit_id_list) for x in xrange(len(circuit_id_list))]
    # break up time period into days
    num_days = dateEnd - dateStart
    beg_day = dateStart
    print len(circuit_id_list)
    for k in range(num_days.days):
        for i,c in enumerate(circuit_id_list):
            print c
            errortimes = inspectDayOfWatthours(c, beg_day)
            if len(errortimes)>0:
                #remove times from dates
                errordates=[]
                for k in range(len(errortimes)):
                    #errordates = errortimes[i].strftime('%Y,%m,%d')
                    #errordates[k] = dt.datetime(....)
                    cctdates[i].append(dt.datetime(errortimes[k].year, errortimes[k].month, errortimes[k].day))
        beg_day = beg_day + dt.timedelta(days=1)
    print cctdates
    for i,c in enumerate(circuit_id_list):
        if cctdates[i]:                 #if there are entries for that cct
            for k in range(len(cctdates[i])):
                plotDatasForCircuit(c, cctdates[i][k], cctdates[i][k] + dt.timedelta(days=1), titleString='whdrops/cct '+str(c)+'on'+str(cctdates[i][k].date()))
