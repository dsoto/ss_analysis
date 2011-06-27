from sql.analysis import *

import datetime as dt

def writeMessageRateOfMeters(dateStart=dt.datetime(2011,6,24), dateEnd=today, fullWrite=False):
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
            #mrate = []
            #for i,c in enumerate(circuit_id_list):
            for m in range(len(meters)):
                mrate=[]
                avg_mrate =[]
                circuit_id_list = getCircuitsForMeter(meters[m])
                for i,c in enumerate(circuit_id_list):
                    dates, data = getDataListForCircuit(c, currentDate, currentDate+dt.timedelta(days=1))
                    mrate.append(len(dates)/24.0)
                    avg_mrate.append(sum(mrate)/len(mrate))
                f.append(currentDate, meters[m], sum(avg_mrate)/len(avg_mrate))
                currentDate += dt.timedelta(days=1)
    else:
        f = open(filename, 'w')
        currentDate = dateStart
        while currentDate < dateEnd:
            for m in range(len(meters)):
                mrate=[]
                circuit_id_list = getCircuitsForMeter(meters[m])
                avg_mrate=[]
                for i,c in enumerate(circuit_id_list):
                    #mrate = []
                    dates, data = getDataListForCircuit(c, currentDate, currentDate+dt.timedelta(days=1))
                    mrate.append(len(dates)/24.0)
                    avg_mrate.append(sum(mrate)/len(mrate))
                stringline = str(currentDate), str(meters[m]), str(sum(avg_mrate)/len(avg_mrate))
                f.write(stringline)
                currentDate += dt.timedelta(days=1)
    f.close()

def printEnergyUsedPerDayByCircuitsOnMeter(circuit_id_list, dateStart=dateStart, dateEnd=dateEnd):
    dataList = np.array([])
    for i,c in enumerate(circuit_id_list):
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        dataList = np.append(dataList, data)
        print c, dates[0].date(), data[0]