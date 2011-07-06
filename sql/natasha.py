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

def watthourCreditMismatches(meters=[4,6,7,8], dateStart=dt.datetime(2011,6,1), dateEnd=today):
    filename = str(meters) + str(dateStart.date()) + '_to_' + str(dateEnd.date()) + '.csv'
    f = open(filename, 'w')
    header = ['date', 'meter', 'circuit', 'watthour', 'credit', 'wh diffs', 'credit diffs, nm']
    for i in range(len(header)):
        f.write(header[i])
        f.write('\t')
    f.write('\n')

    # change for meter locations/rates
    dayrate = 2.0
    nightrate = 2.5

    currentDate=dateStart
    while currentDate < dateEnd:
        #f.write(str(currentDate)); f.write('\t')
        for m in range(len(meters)):
            #f.write(getMeterName(meters[m])); f.write('\t')
            circuits = getCircuitsForMeter(meters[m])
            for c in circuits:
                if session.query(Circuit).filter(Circuit.id == c)[0].ip_address == '192.168.1.200':
                    circuits.remove(c)
            for i,c in enumerate(circuits):
                dates,data=getDataListForCircuit(c,currentDate,currentDate+dt.timedelta(days=1), quantity='watthours')
                c_dates,c_data=getDataListForCircuit(c,currentDate,currentDate+dt.timedelta(days=1), quantity='credit')
                '''
                #check if number of wh and credit messages match up
                if not len(dates) == len(c_dates):
                    print('extra or missing data...first occuring at: ')
                    #find outlier
                    dates_num = matplotlib.dates.date2num(dates)
                    c_dates_num = matplotlib.dates.date2num(c_dates)
                    mask = np.setmember1d(dates_num, c_dates_num)
                    if len(dates_num)>len(cdates_num):
                        if len(set(dates_num)) == len(c_dates_num):
                            for i in range(len(dates_num)-1):
                                if dates_num[i] == dates_num[i+1]:
                                    ind = i
                                    break
                            print 'we have duplicate message/s at ' + matplotlib.dates.num2date(dates_num[ind])
                        else:
                            print matplotlib.dates.num2date(dates_num[np.where(mask==False)][0])
                    elif len(dates_num)<len(c_dates_num):
                        print matplotlib.dates.num2date(c_dates_num[np.where(mask==False)][0])
                    else: print matplotlib.dates.num2date(dates_num[np.where(mask==False)])
                    break
                    '''
                #else:
                '''
                #remove last report per day?
                data=np.delete(data,len(data)-1)
                c_data=np.delete(c_data,len(c_data)-1)
                '''
                if len(dates)==0:
                    break
                #convert credit back to wh
                chours= [x.hour for x in c_dates]
                #am = chours.index(6)
                #am = chours.index(>6)
                #pm = chours.index(>18)
                chours = np.array(chours)
                am = np.where((chours>=6)&(chours<18))
                #if len(am[0])==0:
                    #break
                #print am
                #print am[0]
                #print am[0][0]
                amlist=[]
                for x in range(len(am[0])):
                    amlist.append(am[0][x])
                #print amlist
                pm = np.where((chours<6)|(chours>=18))
                #print pm
                pmlist =[]
                for y in range(len(pm[0])):
                    pmlist.append(pm[0][y])
                #pm = np.where(chours >= 18)
                #c_data[am:pm] = [x*(-(1.0/dayrate)) for x in c_data[am:pm]]
                '''
                for x in range(len(amlist)):
                    c_data[amlist[x]] *= -(1.0/dayrate)
                for x in range(len(pmlist)):
                    c_data[pmlist[x]] *= -(1.0/nightrate)
                    '''
                #c_data[pm] = [x*(-(1.0/nightrate)) for x in c_data[pm]]
                #night = range(0,am) + range(pm, len(c_dates))
                #c_data[0:am] = [x*(-(1.0/nightrate)) for x in c_data[0:am]]
                #c_data[pm:len(c_dates)] = [x*(-(1.0/nightrate)) for x in c_data[pm:len(c_dates)]]
                datadiffs = np.diff(data)
                datadiffs=np.insert(datadiffs, 0, 0)
                creditdiffs = np.diff(c_data)
                #print creditdiffs
                creditdiffs=np.insert(creditdiffs, 0, 0)
                #print c
                #print creditdiffs
                #print amlist
                #print pmlist
                for x in range(len(amlist)):
                    creditdiffs[amlist[x]] *= -(1.0/dayrate)
                for x in range(len(pmlist)):
                    creditdiffs[pmlist[x]] *= -(1.0/nightrate)
                # catch credit jumps
                # would be better to check against logged purchases...
                #cjumps = creditdiffs <0 #negative now that we converted above...
                #notcjump = creditdiffs>0
                for k in range(len(datadiffs)):
                    #if notcjump[k] == True:
                    if creditdiffs[k] > 0:
                        tol = 2
                        if datadiffs[k] < (creditdiffs[k] - tol):
                            print 'cct ' + str(c)+' did not get as many wh as paid on ' + str(dates[k])
                            f.write(str(dates[k])); f.write('\t')
                            f.write(getMeterName(meters[m])); f.write('\t')
                            f.write(str(c));f.write('\t')
                            f.write(str(data[k])); f.write('\t')
                            f.write(str(c_data[k])); f.write('\t')
                            f.write(str(datadiffs[k])); f.write('\t')
                            f.write(str(creditdiffs[k])); f.write('\t')
                            f.write('\n')
                        elif datadiffs[k] > (creditdiffs[k] +tol):
                            print 'cct '+ str(c)+' got more wh than paid for on ' + str(dates[k])
                            f.write(str(dates[k])); f.write('\t')
                            f.write(getMeterName(meters[m])); f.write('\t')
                            f.write(str(c));f.write('\t')
                            f.write(str(data[k])); f.write('\t')
                            f.write(str(c_data[k])); f.write('\t')
                            f.write(str(datadiffs[k])); f.write('\t')
                            f.write(str(creditdiffs[k])); f.write('\t')
                            f.write('\n')
                        #else:
                            #f.write('\n')
                #f.write('\n')
        currentDate += dt.timedelta(days=1)





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
