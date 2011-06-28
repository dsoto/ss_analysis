from sql.analysis import *

import datetime as dt

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
