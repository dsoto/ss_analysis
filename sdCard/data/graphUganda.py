
import sqlite3, sys
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates
import numpy

db = 'uganda002.db'

def getRawDataForCircuit(circuit,
                         timeStart=datetime(2011,6,2),
                         timeEnd=datetime(2011,6,29)):

    con = sqlite3.connect(db, detect_types = sqlite3.PARSE_COLNAMES)
    sql = "select timestamp as 'ts [timestamp]',watthours_today,credit from logs where circuitid=%s and timestamp between '%s' and '%s' order by timestamp asc;" % (circuit, timeStart, timeEnd)

    dates = []
    data = []
    credit = []

    for i, row in enumerate(con.execute(sql)):
        dates.append(row[0])
        data.append(row[1])
        credit.append(row[2])
    con.close()

    # what if no data?

    dates = numpy.array(dates)
    data = numpy.array(data)
    credit = numpy.array(credit)

    return dates, data, credit


def getCleanDataForCircuit(circuit,
                           timeStart,
                           timeEnd):
    dates, data, credit = getRawDataForCircuit(circuit, timeStart, timeEnd)


    wh_drops = numpy.diff(data)
    drop_indices = numpy.where(wh_drops < 0)[0]
    for di in drop_indices:
        data[di+1:] += data[di] - data[di+1]

    # what if no data?

    return dates, data, credit

def getDecimatedDataForCircuit(circuit,
                               timeStart,
                               timeEnd,
                               downsample=20):
    dates, data, credit = getRawDataForCircuit(circuit, timeStart, timeEnd)

    index = range(0, data.shape[0], downsample)
    dates = dates[index]
    data = data[index]
    credit = credit[index]

    return dates, data, credit

def calculateDailyEnergyForCircuit(circuit,
                                   timeStart=datetime(2011,6,2),
                                   timeEnd=datetime(2011,6,3)):
    print str(circuit) + ',',
    current = timeStart
    while current < timeEnd:
        dates, data, credit = getCleanDataForCircuit(circuit, current, current + timedelta(days=1))
        # what if no data?
        #print current,
        if len(data) > 0:
            print str(max(data)) + ',',
        else:
            print 'ND,',
        #print current, current + timedelta(days=1)
        current += timedelta(days=1)
    print

def calculate_30_day_stats_for_circuit():
    pass

def graphPower(circuit,
               timeStart=datetime(2011,6,2),
               timeEnd=datetime(2011,6,29),
               plot_file_name=None):
    print 'graphPower', circuit, timeStart, timeEnd

    dates, data, credit = getCleanDataForCircuit(circuit, timeStart, timeEnd)
    #dates, data, credit = getDecimatedDataForCircuit(circuit, timeStart, timeEnd)

    data = numpy.diff(data)

    # convert dates to seconds
    dates = matplotlib.dates.date2num(dates)

    delta_t = numpy.diff(dates)

    power = data / (delta_t * 24.0)

    fig = plt.figure()
    ax = fig.add_axes((0.1,0.2,0.8,0.7))
    ax.plot(power, 'kx')
    ax.set_ylabel("Power")
    ax.set_xlabel("Time (hours passed)")
    ax.set_title("Circuit %s between %s and %s" % (circuit, timeStart, timeEnd))
    fig.autofmt_xdate()
    if plot_file_name==None:
        plot_file_name = 'power '+str(circuit)+'.pdf'
    fig.savefig(plot_file_name)




def graphDailyWattHours(circuit,
                        timeStart=datetime(2011,6,2),
                        timeEnd=datetime(2011,6,29),
                        plot_file_name=None):
    print "fetching"
    '''
    con = sqlite3.connect(db, detect_types = sqlite3.PARSE_COLNAMES)
    sql = "select timestamp as 'ts [timestamp]',watthours_sc20,credit from logs where circuitid=%s and timestamp between '%s' and '%s' order by timestamp asc;" % (circuit, timeStart, timeEnd)

    dates = []
    data = []
    credit = []

    for i, row in enumerate(con.execute(sql)):
        if i%100 == 0:
            dates.append(row[0])
            data.append(row[1])
            credit.append(row[2])
    con.close()
    '''
    dates, data, credit = getCleanDataForCircuit(circuit, timeStart, timeEnd)
    #dates, data, credit = getRawDataForCircuit(circuit, timeStart, timeEnd)
    dates = matplotlib.dates.date2num(dates)

    print "plotting"
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.2,0.8,0.7))
    ax.plot_date(dates, data, 'kx')
    #ax.plot_date(dates, credit, 'kx')
    ax.set_ylabel("Watt Hours")
    #ax.set_ylabel("Credit")
    ax.set_xlabel("Time (hours passed)")
    ax.set_title("Circuit %s between %s and %s" % (circuit, timeStart, timeEnd))
    fig.autofmt_xdate()
    if plot_file_name==None:
        plot_file_name = 'uganda'+str(circuit)+'.pdf'
    fig.savefig(plot_file_name)

    print "done."

if __name__ == "__main__":
    cid_list = range(1,22)
    for cid in cid_list:
        #graphDailyWattHours(cid, datetime(2011,6,2), datetime(2011,6,29), plot_file_name='clean'+str(cid)+'.pdf')
        calculateDailyEnergyForCircuit(cid, datetime(2011,6,2), datetime(2011,6,29))