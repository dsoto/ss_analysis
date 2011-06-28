from sql.analysis import *

import datetime as dt

def calculateEuclidianDistance(powerVector1, powerVector2):
    return sum((powerVector2 - powerVector1)**2)**(0.5)


def lookForBadSC20(circuit_id,
                   dateStart=dt.datetime(2011,5,1),
                   dateEnd = dt.datetime(2011,6,1)):
    # get all primary parameters in date range
    # loop over primary parameters and look for condition watthours>0 and credit<=0
    # if true print date and circuit_id to console
    logs = session.query(PrimaryLog)\
                  .filter(PrimaryLog.circuit_id == circuit_id)\
                  .filter(PrimaryLog.date > dateStart)\
                  .filter(PrimaryLog.date <= dateEnd)\
                  .order_by(PrimaryLog.created)
    logList = []
    for log in logs:
        if log.watthours > 0 and log.status == 0:
            logList.append((log.date, log.circuit_id, log.watthours, log.status, log.credit))
    logList = list(set(logList))
    logList.sort()

    cw = 20
    print 'date'.rjust(cw),
    print 'circuit id'.rjust(cw),
    print 'watthours'.rjust(cw),
    print 'status'.rjust(cw),
    print 'credit'.rjust(cw)
    for log in logList:
        for l in log:
            print str(l).rjust(cw),
        print

cid = 25

def dailyReportForAllCircuits():
    '''
    prints a graph for each circuit available to be reviewed manually
    '''

    # get yesterdays date
    # this is bad, specify date soon
    date = dt.datetime.now()
    date = dt.datetime(date.year, date.month, date.day) - dt.timedelta(days=1)
    print date

    # get a complete circuit list
    circuits = session.query(Circuit).order_by(Circuit.id)
    circuits = [c.id for c in circuits]

    print circuits

    #circuits = circuits[0:3]

    #plotDatasForCircuit(70, date, date+dt.timedelta(days=1), introspect=True)

    for cid in circuits:
        plotDatasForCircuit(cid,
                            date, date+dt.timedelta(days=1),
                            titleString=str(cid))


if __name__ == "__main__":
    '''
    vector1 = getAveragedPowerForCircuit(cid,
                                         dt.datetime(2011, 06, 20),
                                         dt.datetime(2011, 06, 27))
    print vector1

    vector2 = getAveragedPowerForCircuit(cid,
                                         dt.datetime(2011, 06, 26),
                                         dt.datetime(2011, 06, 27))
    print vector2

    print calculateEuclidianDistance(vector1, vector2)
    '''
    dailyReportForAllCircuits()