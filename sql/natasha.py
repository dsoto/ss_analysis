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
    ax.set_ylim((0,1.1))
    ax.set_ylabel("% messages received")
    #ax.set_xlabel("Date")
    plt.setp(ax.get_xticklabels(), rotation=30)
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
    header = ['date', 'meter', 'circuit', 'watthour', 'credit', 'wh diffs', 'credit diffs, nm' , 'size of diff', 'creditjump', 'notes']
    for i in range(len(header)):
        f.write(header[i])
        f.write('\t')
    f.write('\n')


    currentDate=dateStart
    while currentDate < dateEnd:
        #f.write(str(currentDate)); f.write('\t')
        for m in range(len(meters)):
            #f.write(getMeterName(meters[m])); f.write('\t')
            circuits = getCircuitsForMeter(meters[m])
            # meter locations/rates:  currency per watthour
            dayrate = 2.0
            nightrate = 2.5
            #for uganda rates
            if meters[m] == 6:
                #print 'using uganda rates'
                dayrate = 8.0
                nightrate = 10.0
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
                if len(dates)<12:   #do not run script on days with less than 12 reports...
                    break
                #convert credit back to wh
                chours= [x.hour for x in c_dates]
                chours = np.array(chours)
                #insert zero at beginning............
                #chours = np.insert(chours, 0, 0)
                am = np.where((chours>=6)&(chours<18))
                amlist=[]
                for x in range(len(am[0])):
                    amlist.append(am[0][x])
                pm = np.where((chours<6)|(chours>=18))
                pmlist =[]
                for y in range(len(pm[0])):
                    pmlist.append(pm[0][y])
                # insert zero at beginning of watthour data
                data = np.insert(data, 0, 0)
                # insert previous midnight's data at beginning of credit data
                prev_cdate, prev_cdata = getDataListForCircuit(c, currentDate+dt.timedelta(days=-1), currentDate, quantity='credit')
                if len(prev_cdata) > 1:
                    prevdayshrs = [x.hour for x in prev_cdate]
                    if  prevdayshrs[-1] == 0 or 23:
                        c_data = np.insert(c_data, 0,prev_cdata[len(prev_cdata)-1])
                    else:
                        c_data = np.insert(c_data, 0, c_data[0])
                else:
                    c_data = np.insert(c_data, 0, c_data[0])
                datadiffs = np.diff(data)
                #datadiffs=np.insert(datadiffs, 0, 0)
                creditdiffs = np.diff(c_data)
                #creditdiffs=np.insert(creditdiffs, 0, 0)
                for x in range(len(amlist)):
                    creditdiffs[amlist[x]] *= -(1.0/dayrate)
                for x in range(len(pmlist)):
                    creditdiffs[pmlist[x]] *= -(1.0/nightrate)
                # catch credit jumps
                # would be better to check against logged purchases...
                #cjumps = creditdiffs <0 #negative now that we converted above...
                for k in range(len(datadiffs)):
                    if k==0 and chours[k]>6:
                        break   #don't bother with bad/late starts after 6am
                    # check that it's not a credit jump hour
                    if creditdiffs[k] >= 0:
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
                            f.write(str(creditdiffs[k]-datadiffs[k])); f.write('\t')
                            if chours[k]==0 and datadiffs[k]<0:
                                f.write('\t');f.write('midnight wh drop?'); f.write('\t')
                            else:
                                if 6<=chours[k]<18:
                                    rate = dayrate
                                    wrongrate = nightrate
                                else:
                                    rate = nightrate
                                    wrongrate = dayrate
                                if (c_data[k+1]-c_data[k])*(-1.0/rate) == creditdiffs[k] and datadiffs[k]-0.1<(c_data[k+1]-c_data[k])*(-1.0/wrongrate)<(datadiffs[k]+0.1):
                                    print 'wrong rate used'
                                    f.write('\t');f.write('wrong rate used!')
                                elif datadiffs[k]==0 and k==0:
                                    print 'most likely late start report error'
                                    f.write('\t');f.write('late start report error?')
                                else:
                                    f.write('\t');f.write('original credit diff: ' + str(c_data[k+1]-c_data[k])+' at hour '+str(chours[k])); f.write('\t')
                                    #f.write('hour: ' + str(chours[k])); f.write('\t')
                                    #f.write('chours: ' + str(chours) + ', am: ' + str(amlist) + ' pm: ' + str(pmlist))
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
                            f.write(str(creditdiffs[k]-datadiffs[k])); f.write('\t')
                            if 6<=chours[k]<18:
                                rate = dayrate
                                wrongrate = nightrate
                            else:
                                rate = nightrate
                                wrongrate = dayrate
                            if (c_data[k+1]-c_data[k])*(-1.0/rate) == creditdiffs[k] and (datadiffs[k]-0.1)<(c_data[k+1]-c_data[k])*(-1.0/wrongrate)<(datadiffs[k]+0.1):
                                print 'wrong rate used'
                                f.write('\t');f.write('wrong rate used!')
                            else:
                                f.write('\t');f.write('original credit diff: ' + str(c_data[k+1]-c_data[k])+' at hour '+str(chours[k])); f.write('\t')
                            #f.write('\t');f.write('original credit diff: ' + str(c_data[k]-c_data[k-1])); f.write('\t')
                            #f.write('chours: ' + str(chours) + ', am: ' + str(amlist) + ' pm: ' + str(pmlist)); f.write('\t')
                            f.write('\n')
                        #else:
                            #f.write('\n')
                    # if a credit jump hour
                    elif creditdiffs[k] < 0:
                        # go back and check actual credit jump at that time
                        creditjump = c_data[k] - c_data[k-1]
                        if 6<=chours[k] <18:
                            rate = dayrate
                        else: rate=nightrate
                        # check that credit jump is normal range, after adding used credit
                        # over that very hour
                        #if not [.996*j<(creditjump+(rate*datadiffs[k]))<1.004*j for j in range(len([500,1000,1500,2000,2500,4000,5000,7500,10000]))]:
                        if not 498<(creditjump+(rate*datadiffs[k]))<502 and not 996<(creditjump+(rate*datadiffs[k]))<1004 and not 1996<(creditjump+(rate*datadiffs[k]))<2004 and not 2496<(creditjump+(rate*datadiffs[k]))<2504 and not 3996<(creditjump+(rate*datadiffs[k]))<4004 and not 4996<(creditjump+(rate*datadiffs[k]))<5004 and not 9996<(creditjump+(rate*datadiffs[k]))<10004:
                            print 'credit jump on cct ' + str(c) + ' at ' + str(dates[k])+ ' of ' + str(creditjump)
                            f.write(str(dates[k])); f.write('\t')
                            f.write(getMeterName(meters[m])); f.write('\t')
                            f.write(str(c));f.write('\t')
                            f.write(str(data[k])); f.write('\t')
                            f.write(str(c_data[k])); f.write('\t')
                            f.write(str(datadiffs[k])); f.write('\t')
                            f.write(str(creditdiffs[k])); f.write('\t'); f.write('\t')
                            f.write(str(creditjump)); f.write('\t');
                            f.write('credit jump outside normal range'); f.write('\t');
                            f.write('\n')

                #f.write('\n')
        currentDate += dt.timedelta(days=1)
    f.close()

def plotActualAndPredictedCredit(circuit_id, dateStart, dateEnd=dateStart+dt.timedelta(days=1)):

    currentDate = dateStart
    print dateStart
    print dateEnd
    #actual=[[],[]]
    actual=[]
    predicted=[]
    # meter locations/rates:  currency per watthour
    dayrate = 2.0
    nightrate = 2.5
    #for uganda rates
    if circuit_id in uganda002:
        print 'using uganda rates'
        dayrate = 8.0
        nightrate = 10.0
    hourList=[]
    dayhrs = range(1,24)+[0]
    while currentDate < dateEnd:
        #hourList.append([dayhrs[x] for x in range(len(dayhrs))])
        for x in range(len(dayhrs)):
            hourList.append(dayhrs[x])
        adates, adata = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity='credit')
        whdates, whdata = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity='watthours')
        if len(adates)==0:
            print 'no data on '+str(currentDate)
            break
        #actual[0].append(adates)
        actual.append([adata[x] for x in range(len(adata))])
        hours= [x.hour for x in adates]
        hours = np.array(hours)
        am = np.where((hours>=6)&(hours<18))
        amlist=[]
        for x in range(len(am[0])):
            amlist.append(am[0][x])
        pm = np.where((hours<6)|(hours>=18))
        pmlist =[]
        for y in range(len(pm[0])):
            pmlist.append(pm[0][y])
        # insert zero at beginning of watthour data
        whdata = np.insert(whdata, 0, 0)
        # insert previous midnight's data at beginning of credit data
        prev_cdate, prev_cdata = getDataListForCircuit(circuit_id, currentDate+dt.timedelta(days=-1), currentDate, quantity='credit')
        if len(prev_cdata) > 0:
            prevdayshrs = [x.hour for x in prev_cdate]
            if  prevdayshrs[-1] == 0 or 23:
                adata = np.insert(adata, 0,prev_cdata[len(prev_cdata)-1])
            else:
                adata = np.insert(adata, 0, c_data[0])
        else:
            adata = np.insert(adata, 0, c_data[0])
        datadiffs = np.diff(whdata)
        #set up converted datadiffs:
        conv_datadiffs = datadiffs
        creditdiffs = np.diff(adata)
        for x in range(len(amlist)):
            conv_datadiffs[amlist[x]] /= -(1.0/dayrate)
        for x in range(len(pmlist)):
            conv_datadiffs[pmlist[x]] /= -(1.0/nightrate)
        # start predicted data with first credit value
        pdata = []
        #data.append(adata[0])
        for k in range(len(datadiffs)):
            # check for credit jumps
            cjump = 0
            if creditdiffs[k]>0:
                creditjump = adata[k+1] - adata[k]
                print 'should be equal: '+str(creditdiffs[k])+', and '+str(creditjump)
                if 6<= hours[k] <18:
                    rate = dayrate
                else: rate=nightrate
                # check that credit jump is normal range, after adding used credit
                for i,j in enumerate([500,1000,1500,2000,2500,4000,5000,10000]):
                    if 0.996*j<(creditjump+(rate*datadiffs[k]))<1.004*j:
                        cjump = j
                        print cjump
            #add credit jump to predicted data
            conv_datadiffs[k] += cjump
            # convert converted datadiffs back to non-diff form for predicted data line
            #if k>0:
                #pdata.append(pdata[k-1]+conv_datadiffs[k-1])
            if k==0:
                pdata.append(adata[0])
            else: pdata.append(pdata[k-1]+conv_datadiffs[k])
        print adata
        print pdata
        print conv_datadiffs
        #predicted[0].append(adates)
        predicted.append([pdata[x] for x in range(len(pdata))])

        currentDate += dt.timedelta(days=1)

    # plot
    fig = plt.figure()
    ax = fig.add_axes((.1,.3,.8,.6))
    dates = matplotlib.dates.date2num(adates)
    if len(dates)==0:
        print 'no data...'
    print len(dates)
    print actual
    print predicted
    ax.plot_date(dates, actual[0], 'x-', ms=8, color='blue', label='actual')
    ax.plot_date(dates, predicted[0], 'o-', ms=3, color='r', label='predicted')
    ax.legend(loc=0)
    titleString = 'actual_and_predicted_credit_on_'+str(circuit_id)+'-' + dateStart.date().__str__() + '_to_' + dateEnd.date().__str__()
    ax.set_title(titleString)
    ax.set_ylabel("credit")
    ax.set_xlabel("time")
    #ax.set_xticklabels([adates[x].hour for x in range(len(adates))], fontproperties=textFont, rotation=45)
    #ax.set_xticklabels(ax.get_xticklabels(), fontproperties=textFont, rotation=45)
    plt.setp(ax.get_xticklabels(), fontproperties=textFont)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotActualAndPredictedCredit.__name__)
    annotation.append('circuit = ' + str(circuit_id))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)
    #plt.show()
    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    plotFileName = titleString + '.pdf'
    fig.savefig(plotFileName, transparent=True)

    #plot difference
    fig2 = plt.figure()
    ax2 = fig2.add_axes((.1,.3,.8,.6))
    act_pred_diff=[]
    for a in range(len(datadiffs)):
        act_pred_diff.append(datadiffs[a]-creditdiffs[a])
    print act_pred_diff
    ax2.plot_date(dates, act_pred_diff, '*-', ms=5, color='b', label='difference')
    titleString2 = 'actual-predicted_credit_diff_on_'+str(circuit_id)+'-' + dateStart.date().__str__() + '_to_' + dateEnd.date().__str__()
    ax2.set_title(titleString2)
    ax2.set_ylabel("credit difference")
    ax2.set_xlabel("time")
    plt.setp(ax2.get_xticklabels(), fontproperties=textFont)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotActualAndPredictedCredit.__name__)
    annotation.append('circuit = ' + str(circuit_id))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)
    #plt.show()
    fig2.text(0.01,0.01, annotation) #, fontproperties=textFont)
    plotFileName2 = titleString2 + '.pdf'
    fig2.savefig(plotFileName2, transparent=True)


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
    numPlotsX = 4
    numPlotsY = 3
    if len(circuits)> 12:
        numPlotsX = 4
        numPlotsY = 5
    # need for uganda
    if len(circuits)>20:
        numPlotsX = 5
        numPlotsY = 5

    for i,c in enumerate(circuits):
        calculatedCredits = calculateCreditJumps(c, dateStart, dateEnd, verbose)
        loggedPurchases = calculateCreditPurchase(c, dateStart, dateEnd, verbose)

        dates = np.union1d(calculatedCredits[0], loggedPurchases[0])
        print c
        print dates
        dates = matplotlib.dates.date2num(dates)
        calculatedCreditDates = matplotlib.dates.date2num(calculatedCredits[0])
        mask1 = []
        for l in range(len(calculatedCreditDates)):
            ind = np.where(dates==calculatedCreditDates[l])
            #print ind
            mask1.append(int(ind[0]))       #because ind was an array of arrays!
        #mask1 = np.where(dates,calculatedCredits[0])
        #mask1 = np.setmember1d(dates, calculatedCredits[0])    #mergesort not avail for type
        data1 = [-1000]*len(dates)
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
        data2 = [-1000]*len(dates)
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
        #thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1, xlim=(dateStart, dateEnd), ylim=(0,1100)) #to keep all plots even, assuming 1100 is enough
        data12 = []
        if len(data1)>0:
            for x in range(len(data1)):
                data12.append(data1[x])
        if len(data2)>0:
            for x in range(len(data2)):
                data12.append(data2[x])
        if len(data12)>0:
            ymax = max(data12)
            #ymax = max(data1.extend([data2[x] for x in range(len(data2))]))
        else: ymax = 1100
        ymax = max(ymax, 1100)
        if 1100<ymax<2100:
            ymax = 2100
        if 2100<ymax<2600:
            ymax = 2600
        if 2600<ymax<1300:
            ymax=3100

        thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1, xlim=(dateStart, dateEnd), ylim=(0,ymax))
        thisAxes.plot_date(dates, data1, ls=' ', ms=7, marker='o', c='b')
        thisAxes.plot_date(dates, data2, ls=' ', ms=12, marker='x', c='r')
        #from matplotlib import font_manager
        #smallsize = font_manager.FontProperties(size=mpl.rcParams['font.size'])
        thisAxes.set_xticklabels(dateList, fontproperties=textFont)
        #thisAxes.set_yticklabels(yLabels, fontproperties=textFont)
        plt.setp(thisAxes.get_yticklabels(), fontproperties=textFont)
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
    if isinstance(meters, int) is False:
        circuit_id_list=[]
        for m in range(len(meters)):
            ccts = getCircuitsForMeter(meters[m])
            #print ccts
            for x in range(len(ccts)):
                circuit_id_list.append(ccts[x])
    else: circuit_id_list = getCircuitsForMeter(meters)
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

def flashlight():

    voltage = np.flipud(np.arange(1.0,3.3,0.1))
    voltage = np.delete(voltage, [2,16])  # take out 3. and 1.6 that didnt have direct data
    current = [129,109, 90, 73, 60, 50.5, 45.75, 45.5, 46.1, 45.8, 44.8, 42.8, 40, 37.4, 35.1, 33.25, 32.5, 33.6, 32.1, 23.5, 10.4]
    lux = [2700,2500,2290,2000,1705,1444,1272,1218,1186,1134,1065,982,891,800,715,642,571,459,253,95,12]
    distance = np.arange(0,24,1)
    lux_at_d = [2570,2020,1270,563,282,180,120,86,67,55,48,41,37,33,30,28,24,18,11,8,6,4,2,0]

    fig=plt.figure()
    fig,axs = plt.subplots(3,1)
    axs[0].plot(voltage, current)
    axs[0].invert_xaxis()
    axs[0].set_title('I-V curve')
    axs[1].plot(voltage, lux)
    axs[1].invert_xaxis()
    axs[1].set_title('lux vs. voltage')
    axs[2].plot(distance, lux_at_d)
    axs[2].set_title('lux vs. horizontal distance, at 25cm height')
    fig.savefig('flashlight.pdf')

def powerReadings():

    circuits = [201,202,203,204]
    res = [5000, 2500, 1000, 500]
    res_watts = [(np.square(120.0)/res[x]) for x in range(len(res))]
    loads = [0] + res_watts

    main_read = np.zeros((len(circuits), len(res_watts)))
    main_noload = [38.05,37.8,37.95,38.05]
    main_read[0] = [41.4,44.65,54.45,70.6]
    main_read[1] = [41.0,44.3,54.0,70.4]
    main_read[2] = [41.35,44.6,54.25,70.55]
    main_read[3] = [41.35,44.65,54.25,70.6]
    for i in range(len(main_read)):
        main_read[i] = main_read[i] - main_noload
    print main_read
    cct_read = np.zeros((len(circuits), len(res_watts)))
    cct_read[0] = [2.2,5.55,15.25,32]
    cct_read[1] = [2.85,6.1,15.75,31.9]
    cct_read[2] = [2.85,6.2,15.85,32.25]
    cct_read[3] = [2.75,6.1,15.85,32.1]
    #cctreads = np.zeros((len(circuits), len(loads)))
    for i in range(len(loads)):
        cctreads = np.insert(cct_read, 0, 0, 1)
    print cctreads
    fig=plt.figure()
    ax = fig.add_axes((.1,.3,.8,.6))
    #fig,axs = plt.subplots(2,1)
    for i in range(len(main_read)):
        ax.plot(res_watts, main_read[i]-cct_read[i], 'x-', label=str(circuits[i]))
    ax.legend(loc=0)
    ax.set_xlabel("load (watts)")
    ax.set_ylabel("difference (watts)")
    ax.set_title("difference between circuit and main meter readings")
    fig.savefig('powerReadingDiffs.pdf')
    fig2=plt.figure()
    ax2 = fig2.add_axes((.1,.3,.8,.6))
    #fig,axs = plt.subplots(2,1)
    for i in range(len(cctreads)):
        ax2.plot(loads, cctreads[i]-loads, 'x-', label=str(circuits[i]))
    ax2.legend(loc=0)
    ax2.set_xlabel("loads (watts)")
    ax2.set_ylabel("difference (watts)")
    ax2.set_title("difference between measured and real power")
    fig2.savefig('readingdiffs.pdf')

def plotSelfConsumption(meter_id=8,
                        dateStart=dt.datetime(2011, 7, 1),
                        dateEnd=dt.datetime(2011, 7, 8),
                        num_drop_threshold=1,
                        num_samples_threshold=16,
                        verbose=0):

    tw.log.info('entering plotSelfConsumption')

    meter = session.query(Meter).get(meter_id)
    mains_id = meter.getMainCircuit().id
    customer_circuit_list = [c.id for c in meter.getConsumerCircuits()]

    tw.log.info('mains circuit = ' + str(mains_id))
    tw.log.info('customer circuits = ' + str(customer_circuit_list))
    print 'total # of circuits = ',len(customer_circuit_list)
    expectedMainsWatts_allon = 12.6+2.6+(len(customer_circuit_list)*(2.6-1.35))
    expectedMainsWatthours_allon = expectedMainsWatts_allon*24
    expectedMainsWatts_alloff = 12.6+2.6+(len(customer_circuit_list)*(2.6))
    expectedMainsWatthours_alloff = expectedMainsWatts_alloff*24
    #expMainsOn = np.ones((dateEnd-dateStart).days)*expectedMainsWatthours_allon
    #expMainsOff = np.ones((dateEnd-dateStart).days)*expectedMainsWatthours_alloff
    print 'mains expected to consume between ', expectedMainsWatthours_allon, ' and ', expectedMainsWatthours_alloff, ' wh per day'

    # loop through days
    # for each day total household consumption and infer mains consumption
    # create list of dates, household consumption and mains consumption
    dates = []
    household_consumption = []
    mains_consumption = []
    perc_ccts_off=[]
    number_ccts_off=[]

    fig = plt.figure()
    #ax = fig.add_axes((0.1,0.1,0.8,0.8))
    ax = fig.add_axes((.1,.3,.8,.6))

    current_date = dateStart
    while current_date < dateEnd:

        print current_date
        mains_energy = getEnergyForCircuitForDayByMax(mains_id, current_date)
        print 'mains energy =', mains_energy[0]

        total_energy = 0
        num_ccts_off=0
        for cid in customer_circuit_list:

            customer_energy = getEnergyForCircuitForDayByMax(cid,
                                             current_date)
            #print customer_energy[0]
            if customer_energy[0]==0:
                # better to check if credit is 0 at same time
                c_dates, credit = getDataListForCircuit(cid,current_date,current_date+dt.timedelta(days=1),quantity='credit')
                if np.average(credit)<1:
                    num_ccts_off +=1
            total_energy += customer_energy[0]

        print 'total energy =', total_energy
        perc_ccts_off.append(num_ccts_off/float(len(customer_circuit_list)))
        number_ccts_off.append(num_ccts_off)


        if mains_energy[1] > num_samples_threshold and mains_energy[2] < num_drop_threshold and mains_energy[0]>total_energy:
            dates.append(current_date)
            mains_consumption.append(mains_energy[0] - total_energy)
            household_consumption.append(total_energy)
            tw.log.info(str(current_date))
            tw.log.info('mains energy for day ' + str(mains_energy[0] - total_energy))
            tw.log.info('household consumpition ' + str(total_energy))
        else:
            tw.log.info('rejecting date ' + str(current_date))
            if mains_energy[1] <= num_samples_threshold:
                tw.log.info('rejected for too few samples')
            if mains_energy[2] >= num_drop_threshold:
                tw.log.info('rejected for too many watthour drops')
            if mains_energy[0] < total_energy:
                tw.log.info('rejected for mains < household consumption')

        current_date += dt.timedelta(days=1)

    print mains_consumption
    print 'average mains consumption = ', np.average(mains_consumption)
    dates = matplotlib.dates.date2num(dates)
    expMainsOn = np.ones(len(dates))*expectedMainsWatthours_allon
    expMainsOff = np.ones(len(dates))*expectedMainsWatthours_alloff
    expMains = []
    for i in range(len(dates)):
        expMains.append(24*(12.6+2.6+(len(customer_circuit_list)*2.6) - ((len(customer_circuit_list)-number_ccts_off[i])*1.35)))

    ax.plot_date(dates, household_consumption, 'o-', label='Household Total')
    ax.plot_date(dates, mains_consumption, 'x-', label='Meter Consumption')
    ax.plot_date(dates, expMainsOn, '-', color='0.9')
    ax.plot_date(dates, expMainsOff, '-', color='0.75')
    ax.plot_date(dates, expMains, '-', color='k', label='expected Mains consumption')
    ax.legend()
    ax.set_ylim((0,2000))
    ax.set_xlim((matplotlib.dates.date2num(dateStart), matplotlib.dates.date2num(dateEnd)))
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy Consumption (watthours)')
    fileNameString = 'selfconsumption-' +  ' ' + str(meter_id) + '-' + dateStart.date().__str__() + '_to_' + dateEnd.date().__str__()
    ax.set_title(fileNameString)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotSelfConsumption.__name__)
    annotation.append('meter = ' + str(getMeterName(meter_id)))
    annotation.append('# circuits = ' + str(len(customer_circuit_list)))
    annotation.append('mains expected to consume between ' + str(expectedMainsWatthours_allon) +' and '+str(expectedMainsWatthours_alloff)+ ' wh daily')
    annotation.append('number of circuits off each day = ' + str(number_ccts_off))
    annotation.append('average percentage of circuits off = ' + str(np.round(100*np.average(perc_ccts_off))))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)
    #plt.show()
    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(fileNameString+'.pdf')
    tw.log.info('exiting plotSelfConsumption')

def plotHourlySelfConsumption(meter_id=8,
                        dateStart=dt.datetime(2011, 7, 1),
                        dateEnd=dt.datetime(2011, 7, 8),
                        num_drop_threshold=1,
                        num_samples_threshold=23,
                        verbose=0):

    tw.log.info('entering plotHourlySelfConsumption')

    meter = session.query(Meter).get(meter_id)
    mains_id = meter.getMainCircuit().id
    customer_circuit_list = [c.id for c in meter.getConsumerCircuits()]

    tw.log.info('mains circuit = ' + str(mains_id))
    tw.log.info('customer circuits = ' + str(customer_circuit_list))
    print 'total # of circuits = ',len(customer_circuit_list)
    expectedMainsWatts_allon = 7.3+(2*2.6)+(len(customer_circuit_list)*(2.6-1.35))
    #expectedMainsWatthours_allon = expectedMainsWatts_allon*24
    expectedMainsWatts_alloff = 7.3+(2*2.6)+(len(customer_circuit_list)*(2.6))
    #expectedMainsWatthours_alloff = expectedMainsWatts_alloff*24
    #expMainsOn = np.ones((dateEnd-dateStart).days)*expectedMainsWatthours_allon
    #expMainsOff = np.ones((dateEnd-dateStart).days)*expectedMainsWatthours_alloff
    print 'mains expected to consume between ', expectedMainsWatts_allon, ' and ', expectedMainsWatts_alloff, ' wh per day'

    # loop through days
    # for each day total household consumption and infer mains consumption
    # create list of dates, household consumption and mains consumption
    dates = []
    dates2 = []
    household_consumption = []
    mains_consumption = []
    total_consumption = []
    perc_ccts_off=[]
    number_ccts_off=[]


    fig = plt.figure()
    #ax = fig.add_axes((0.1,0.1,0.8,0.8))
    ax = fig.add_axes((.1,.25,.8,.65))    # used to be (.1, .3, .8, .6)

    current_date = dateStart
    while current_date < dateEnd:

        print current_date
        mains_power = calculatePowerListForCircuit(mains_id, current_date, current_date+dt.timedelta(days=1))
        print 'mains energy =', mains_power[1]

        # add 24 hours for each fully reported day of power
        #allcustomers_power = np.append(allcustomers_power,np.zeros(24))
        allcustomers_power = np.zeros(24)
        num_ccts_off=np.zeros(24)
        for cid in customer_circuit_list:

            customer_power = calculatePowerListForCircuit(cid, current_date, current_date+dt.timedelta(days=1))
            if len(customer_power[1])==24:
                # better to check if credit is 0 at same time
                c_dates, credit = getDataListForCircuit(cid,current_date,current_date+dt.timedelta(days=1),quantity='credit')
                #add cct to 'off' category
                for k in range(len(customer_power[1])):
                    if customer_power[1][k]<0.1 and credit[k]<0.1:
                            num_ccts_off[k] +=1
                            #print 'circuit ', cid, ' is off at ', customer_power[0][k]

                # add to allcustomer power array
                for h in range(24):
                    allcustomers_power[h] += customer_power[1][h]

        #print 'total energy =', total_energy
        perc_ccts_off.append(num_ccts_off/float(len(customer_circuit_list)))
        #number_ccts_off.append(num_ccts_off)


        if len(mains_power[1])==24 and mains_power[2] < num_drop_threshold: # and np.sum(mains_power[1])>np.sum(allcustomers_power):
            dates.append(current_date)
            for x in range(len(num_ccts_off)):
                number_ccts_off=np.append(number_ccts_off, num_ccts_off[x])
            #print number_ccts_off, ' ccts off'
                mains_consumption=np.append(mains_consumption,(mains_power[1] - allcustomers_power)[x])
                total_consumption=np.append(total_consumption,(mains_power[1][x]))
                household_consumption=np.append(household_consumption,allcustomers_power[x])
                dates2=np.append(dates2,mains_power[0][x])
            tw.log.info(str(current_date))
            tw.log.info('mains energy for day ' + str(mains_power[1] - allcustomers_power))
            tw.log.info('household consumpition ' + str(allcustomers_power))
        else:
            tw.log.info('rejecting date ' + str(current_date))
            if len(mains_power[1]) <= num_samples_threshold:
                tw.log.info('rejected for too few samples')
            if mains_power[2] >= num_drop_threshold:
                tw.log.info('rejected for too many watthour drops')
            if np.sum(mains_power[1]) < np.sum(allcustomers_power):
                tw.log.info('rejected for mains < household consumption')

        current_date += dt.timedelta(days=1)


    print mains_consumption
    print 'average mains consumption = ', np.average(mains_consumption)
    hours = []
    for d in range(len(dates)):
        hours = np.append(hours,np.append(np.arange(1,24),0))
    dates = matplotlib.dates.date2num(dates)
    #dates2 = matplotlib.dates.date2num(dates2)
    expMainsOn = np.ones(len(hours))*expectedMainsWatts_allon
    expMainsOff = np.ones(len(hours))*expectedMainsWatts_alloff
    expMains = []
    for i in range(len(hours)):
        expMains.append(7.3+(2*2.6)+(len(customer_circuit_list)*2.6) - ((len(customer_circuit_list)-number_ccts_off[i])*1.35))

    ax.plot(dates2, household_consumption, 'o-', label='Household Total')
    ax.plot(dates2, mains_consumption, 'x-', label='Meter Consumption')
    ax.plot(dates2, total_consumption, '*-', label='Total Consumption')
    ax.plot(dates2, expMainsOn, '-', color='0.9')
    ax.plot(dates2, expMainsOff, '-', color='0.75')
    ax.plot(dates2, expMains, '-', color='k', label='expected Mains consumption')
    ax.legend(loc=0)
    y_high = max(total_consumption)
    ax.set_ylim((0,y_high))
    #ax.set_xlim((matplotlib.dates.date2num(dateStart), matplotlib.dates.date2num(dateEnd)))
    #ax.set_xlabel('Date')
    ax.set_ylabel('Power Consumption (watts)')
    plt.setp(ax.get_xticklabels(), rotation=30)
    fileNameString = 'hourlyselfconsumption-' +  ' ' + str(meter_id) + '-' + dateStart.date().__str__() + '_to_' + dateEnd.date().__str__()
    ax.set_title(fileNameString)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotHourlySelfConsumption.__name__)
    annotation.append('meter = ' + str(getMeterName(meter_id)) + ' with ' + str(len(customer_circuit_list)) + ' # of circuits')
    annotation.append('mains expected to consume between ' + str(expectedMainsWatts_allon) +' and '+str(expectedMainsWatts_alloff)+ ' watts hourly')
    #annotation.append('number of circuits off each day = ' + str(number_ccts_off))
    annotation.append('average percentage of circuits off = ' + str(np.round(100*np.average(perc_ccts_off))))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)
    #plt.show()
    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(fileNameString+'.pdf')
    tw.log.info('exiting plotHourlySelfConsumption')

def plotPowerConsumptionError():
    R = [4980, 9950, 19900, 14200, 2490, 994, 500]
    R = np.flipud(np.sort(R))
    Vrms = 125.0
    pred_power = [np.square(Vrms)/R[x] for x in range(len(R))]
    print pred_power
    belkin = [3.2, 1.6, 0.8, 1.1, 6.3, 15.6, 31.0]
    belkin = np.sort(belkin)
    sc20_1 = [2.3, 0.8, 0, 0, 5.5, 14.8, 30.4]
    sc20_2 = [2.7, 1.1, 0, 0, 5.8, 15.2, 30.8]
    sc20_1 = np.sort(sc20_1)
    sc20_2 = np.sort(sc20_2)
    mains_measured = [31.0, 29.4, 28.6, 29, 34.1, 43.6, 59.5]
    mains_measured = np.sort(mains_measured)
    baseline = np.ones(len(R)) * 27.9
    sc20_mains = mains_measured - baseline

    fig = plt.figure()
    ax = fig.add_axes((.1,.3,.8,.6))
    ax.loglog(pred_power, sc20_mains, 'x-', color='r', label='Mains')
    ax.loglog(pred_power, pred_power, '-', color='k', label='ideal')
    ax.loglog(pred_power, [pred_power[x]*.9 for x in range(len(pred_power))], '-', color='0.75', label='-10%')
    ax.loglog(pred_power, [pred_power[x]*1.1 for x in range(len(pred_power))], '-', color='0.75', label='+10%')
    ax.loglog(pred_power, sc20_1, '^-', color='b', label='sc20_1')
    ax.loglog(pred_power, sc20_2, '^-', color='g', label='sc20_2')
    ax.legend(loc=0)
    ax.set_ylim((0,35))
    ax.set_xlim((0,35))
    ax.set_xlabel('predicted power (watts)')
    ax.set_ylabel('measured power (watts)')
    #ax.set_xticklabels(np.exp(
    fileNameString = 'log-log plot of power measurement error'
    ax.set_title(fileNameString)
    annotation = []
    annotation.append('plot generated ' + today.__str__() )
    annotation.append('function = ' + plotPowerConsumptionError.__name__)
    annotation.append('data points at predicted power of: ' + str(np.round(pred_power,2)))
    annotation = '\n'.join(annotation)
    #plt.show()
    fig.text(0.01,0.01, annotation) #, fontproperties=textFont)
    fig.savefig(fileNameString+'.pdf')
