
import sqlite3, sys
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates
import numpy

db = 'ug02_test.db'

def getRawDataForCircuit(circuit,
                         timeStart=datetime(2011,8,1),
                         timeEnd=datetime(2011,8,3)):

    con = sqlite3.connect(db, detect_types = sqlite3.PARSE_COLNAMES)
    sql = """select timestamp as 'ts [timestamp]',watthours_today,credit,watts
             from logs where circuitid=%s and timestamp between '%s' and '%s'
             order by timestamp asc;""" % (circuit, timeStart, timeEnd)

    dates = []
    data = []
    credit = []
    watts = []

    for i, row in enumerate(con.execute(sql)):
        dates.append(row[0])
        data.append(row[1])
        credit.append(row[2])
        watts.append(row[3])
    con.close()

    # what if no data?

    dates = numpy.array(dates)
    data = numpy.array(data)
    credit = numpy.array(credit)
    watts = numpy.array(watts)
    return dates, data, credit, watts


def getCleanDataForCircuit(circuit,
                           timeStart,
                           timeEnd):
    #dates, data, credit = getRawDataForCircuit(circuit, timeStart, timeEnd)
    dates, data, credit, watts = getDecimatedDataForCircuit(circuit, timeStart, timeEnd)

    wh_drops = numpy.diff(data)
    drop_indices = numpy.where(wh_drops < 0)[0]
    for di in drop_indices:
        data[di+1:] += data[di] - data[di+1]

    # what if no data?

    return dates, data, credit, watts

def getDecimatedDataForCircuit(circuit,
                               timeStart,
                               timeEnd,
                               downsample=20):
    dates, data, credit, watts = getRawDataForCircuit(circuit, timeStart, timeEnd)

    index = range(0, data.shape[0], downsample)
    dates = dates[index]
    data = data[index]
    credit = credit[index]
    watts = watts[index]
    return dates, data, credit, watts


circuit_id = 10
dates, data, credit, watts = getDecimatedDataForCircuit(circuit_id,
                                                        datetime(2011,8,1),
                                                        datetime(2011,8,3),
                                                        downsample=20)

print "dates, watt hours today, credit, watts"
for i in range(len(dates)):
    print dates[i],
    print ',',
    print data[i],
    print ',',
    print credit[i],
    print ',',
    print watts[i]


