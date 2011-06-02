import sqlalchemy
import urllib
import numpy as np
import matplotlib.dates
import matplotlib.pyplot as plt
import datetime as dt

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import Numeric
from sqlalchemy import Unicode

engine = sqlalchemy.create_engine('postgres://postgres:postgres@localhost:5432/gateway')
connection = engine.connect()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker, relation

Session = sessionmaker(bind=engine)

session = Session()

# circuit id's for quick and dirty lists
mali001 = range(13,25)
ml05 = [56, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 77, 93, 95]
ml06 = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 96, 97, 98, 99, 100]


# orm classes

"""
A class that repsents a meter in the gateway
"""
class Meter(Base):
    __tablename__ = 'meter'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    name = Column(String)
    phone = Column(String)
    location = Column(String)
    status = Column(Boolean)
    date = Column(DateTime)
    battery = Column(Integer)
    panel_capacity = Column(Integer)


    def __init__(self, name=None, phone=None, location=None,
                 battery=None, status=None, panel_capacity=None,
                 communication_interface_id=None):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.phone = phone
        self.location = location
        self.date = get_now()
        self.battery = battery
        self.communication_interface_id = communication_interface_id
        self.panel_capacity = panel_capacity

"""
ORM class for the account
"""
class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    lang = Column(String)

    def __init__(self, name="default", phone=None, lang="en"):
        self.name = name
        self.phone = phone
        self.lang = lang

"""
ORM class for circuit
"""
class Circuit(Base):
    __tablename__ = "circuit"

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    date = Column(DateTime)
    pin = Column(String)
    meter_id = Column("meter", ForeignKey("meter.id"))
    meter = relation(Meter,
                      lazy=False, primaryjoin=meter_id == Meter.id)
    energy_max = Column(Float)
    power_max = Column(Float)
    status = Column(Integer)
    ip_address = Column(String)
    credit = Column(Float)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relation(Account, lazy=False,
                        cascade="all,delete",
                        backref='circuit',
                        primaryjoin=account_id == Account.id)

    def __init__(self, meter=None, account=None,
                 energy_max=None, power_max=None,
                 ip_address=None, status=1, credit=0):
        self.date = get_now()
        self.uuid = str(uuid.uuid4())
        self.pin = self.get_pin()
        self.meter = meter
        self.energy_max = energy_max
        self.power_max = power_max
        self.ip_address = ip_address
        self.status = status
        self.credit = credit
        self.account = account

'''
ORM class for base log class.  primary log inherits from this class.
'''
class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)         # this is the time stamp from the meter
    uuid = Column(String)
    _type = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': _type}
    circuit_id = Column(Integer, ForeignKey('circuit.id'))
    circuit = relation(Circuit, lazy=False,
                       primaryjoin=circuit_id == Circuit.id)

    def __init__(self, date=None, circuit=None):
        self.date = date
        self.uuid = str(uuid.uuid4())
        self.circuit = circuit

'''
this inherits from Log
'''
class PrimaryLog(Log):
    __tablename__ = "primary_log"
    __mapper_args__ = {'polymorphic_identity': 'primary_log'}
    id = Column(Integer, ForeignKey('log.id'), primary_key=True)
    watthours = Column(Float)
    use_time = Column(Float)
    status = Column(Integer)
    created = Column(DateTime)
    credit = Column(Float, nullable=True)
    status = Column(Integer)

    def __init__(self, date=None, circuit=None, watthours=None,
                 use_time=None, status=None, credit=0):
        Log.__init__(self, date, circuit)
        self.circuit = circuit
        self.watthours = watthours
        self.use_time = use_time
        self.credit = credit
        self.created = get_now()
        self.status = status

    def getUrl(self):
        return ""

    def getType(self):
        if self.circuit.ip_address == '192.168.1.200':
            return 'MAIN'
        else:
            return 'CIRCUIT'

    def getCreditAndType(self):
        if self.getType() == 'MAIN':
            return [('ct', self.getType()), ('cr', 0)]
        else:
            return [('cr', float(self.credit)), ('ct', self.getType())]

    def __str__(self):
        return urllib.urlencode([('job', 'pp'),
                                 ('status', self.status),
                                 ('ts', self.created.strftime("%Y%m%d%H")),
                                 ('cid', self.circuit.ip_address),
                                 ('tu', int(self.use_time)),
                                 ('wh', float(self.watthours))] + self.getCreditAndType())


# convenience and helper functions

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

def plotDataForCircuit(circuit_id,
                            dateStart=dt.datetime(2011,5,12),
                            dateEnd=dt.datetime(2011,5,13),
                            quantity='watthours',
                            introspect=False):
    dates, data = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity)
    dates = matplotlib.dates.date2num(dates)
    fig = plt.figure()
    ax = fig.add_axes((.2,.2,.6,.6))
    ax.plot_date(dates, data, 'x-')
    titleString = 'circuit ' + str(circuit_id) + quantity
    ax.set_title(titleString)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()
    fig.savefig(titleString + '.pdf')

'''
plot credit or watthours for all circuits on a meter
'''
def plotDataForAllCircuitsOnMeter(meter_id,
                              dateStart=dt.datetime(2011,5,28),
                              dateEnd=dt.datetime(2011,6,1),
                              quantity='credit',
                              introspect=False,
                              showMains=False):

    circuits = getCircuitsForMeter(meter_id)

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

    # loop through circuits, get data, plot
    for i,c in enumerate(circuits):
        dates, data = getDataListForCircuit(c, dateStart, dateEnd, quantity)

        dates = matplotlib.dates.date2num(dates)

        thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1)
        thisAxes.plot_date(dates, data, ls='-', ms=3, marker='o', mfc=None)
        #thisAxes.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=(0)))
        #thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
        thisAxes.text(0.7,0.7,str(c),transform = thisAxes.transAxes)

    fileNameString = 'meter ' + quantity + ' ' + str(meter_id) + '.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(fileNameString)


# printing functions

'''
prints a table of whether or not circuits have reported on certain dates
'''
def printHugeMessageTable(startDate = dt.datetime(2011, 5, 24),
                          endDate   = dt.datetime(2011, 6, 1)):
    import datetime as dt

    circuit = session.query(Circuit).all()

    print len(circuit)

    clist = [c.id for c in circuit]
    clist.sort()
    numCol = max(clist) + 1

    #print clist

    numRow = (endDate - startDate).days * 25

    import numpy as np

    report = np.zeros((numRow, numCol))
    print report.shape
    dates = []
    originalQuery = session.query(PrimaryLog)

    start = startDate
    i = 0
    while 1:
        end = start + dt.timedelta(hours=1)
        thisQuery = originalQuery

        # deal with double report problem

        #if start.hour != 23:
        if 1:
            # take reports in the hour between start and end
            thisQuery = thisQuery.filter(PrimaryLog.date >= start)
            thisQuery = thisQuery.filter(PrimaryLog.date < end)
            #thisQuery = thisQuery.filter(PrimaryLog.date == endDate)
            cclist = [tq.circuit_id for tq in thisQuery]
            cclist.sort()
            # add to numpy array
            report[i,cclist] = 1
            dates.append(start)
            i += 1
            # output to screen
            print start,
            print "".join([str(x).ljust(3) if x in cclist else ' - ' for x in clist])
        '''
        else:
            # change report range to prevent including the 23:59:59 report in the 23:00:00 row
            lastReportTime = dt.datetime(start.year, start.month, start.day, start.hour, 59, 59)
            thisQuery = thisQuery.filter(PrimaryLog.date > start)
            thisQuery = thisQuery.filter(PrimaryLog.date < lastReportTime)
            cclist = [tq.circuit_id for tq in thisQuery]
            cclist.sort()
            # add to numpy array
            report[i,cclist] = 1
            dates.append(start)
            i += 1
            # output to screen
            print start,
            print "".join([str(x).ljust(3) if x in cclist else ' - ' for x in clist])
            # end of day report
            thisQuery = originalQuery
            thisQuery = thisQuery.filter(PrimaryLog.date == lastReportTime)
            cclist = [tq.circuit_id for tq in thisQuery]
            cclist.sort()
            # add to numpy array
            report[i,cclist] = 1
            dates.append(lastReportTime)
            i += 1
            # output to screen
            print lastReportTime,
            print "".join([str(x).ljust(3) if x in cclist else ' - ' for x in clist])
        '''
        start = start + dt.timedelta(hours=1)
        if start >= endDate:
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
                              dateStart=dt.datetime(2011,5,28),
                              dateEnd=dt.datetime(2011,5,29),
                              quantity='watthours',
                              verbose=0):
    # get query based on circuit and date
    # and sort by date received by gateway
    logs = session.query(PrimaryLog)\
                  .filter(PrimaryLog.circuit_id == circuit_id)\
                  .filter(PrimaryLog.date > dateStart)\
                  .filter(PrimaryLog.date <= dateEnd)\
                  .order_by(PrimaryLog.created)

    # create separate arrays for each of these quantities
    dates = np.array([l.date for l in logs])
    data  = np.array([getattr(l, quantity) for l in logs])
    created = np.array([l.created for l in logs])

    # remove midnight sample from the future
    # by creating a boolean mask and then indexing arrays based on that mask
    mask = []
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

    if verbose > 0:
        for d in dataList:
            print d

    return dates, data

'''
checks a watthour list to be sure it has 24 samples and that the watthour
readings are monotonic.
input:
    circuit_id - circuit database id
    date - datetime object
    method - 'max', 'midnight', 'eleven'
output:
    watthours for the day specified by date in input.  returns -1 on error
TODO:
    improve heuristic for estimating usage on days with incomplete data
    currently if there is no data for a day, an error is thrown
'''
def getDailyEnergyForCircuit(circuit_id,
                             date=dt.datetime(2011,5,12),
                             verbose=0,
                             method='max',
                             requireMonotonic=True,
                             monotonicThreshold=-1,
                             reportThreshold=12,
                             strict=True):
    # set date range
    dateStart = date
    dateEnd = dateStart + dt.timedelta(days=1)

    dates, watthours = getDataListForCircuit(circuit_id, dateStart, dateEnd,
                                             verbose=verbose,
                                             quantity='watthours')
    watthours = np.array(watthours)

    # error checking
    isMonotonic = np.alltrue(np.diff(watthours) >= monotonicThreshold)
    numReports = watthours.shape[0]
    has24reports = numReports >= 24

    if (verbose > 1):
        if isMonotonic:
            print 'watthour data monotonic'
        else:
            print 'watthour data non-monotonic'
        print 'number of reports = ', numReports

    if len(watthours) == 0:
        return -1
    else:
        if method == 'max' and requireMonotonic and isMonotonic and numReports > reportThreshold:
            return np.max(watthours)
        if method == 'max' and not requireMonotonic and numReports > reportThreshold:
            return np.max(watthours)
        else:
            return -1

        if method == 'midnight':
            if isMonotonic and has24reports:
                return watthours[-1]
            else:
                return -1
        if method == 'eleven':
            # this is crazy janky
            # hack to return the value before the duplicate midnight samples
            return watthours[-3]

'''
for a given circuit and date range, this function returns the average energy, discarding
days with unsatisfactory data
'''
def getDailyEnergyListForCircuit(circuit_id,
                            dateStart=dt.datetime(2011,4,1),
                            dateEnd=dt.datetime(2011,5,1),
                            method='max',
                            requireMonotonic=True,
                            monotonicThreshold=-1,
                            reportThreshold=12,
                            verbose=0):
    date = dateStart
    dateList = []
    energyList = []
    while date <= dateEnd:
        tempData = getDailyEnergyForCircuit(circuit_id, date, verbose=verbose,
                                                              method='max',
                                                              requireMonotonic=requireMonotonic,
                                                              monotonicThreshold=monotonicThreshold,
                                                              reportThreshold=reportThreshold)
        dateList.append(date)
        energyList.append(tempData)
        date += dt.timedelta(days=1)

    return np.array(dateList), np.array(energyList)

'''
for a given circuit and date range, this function returns the average energy, discarding
days with unsatisfactory data
'''
def calculateAverageEnergyForCircuit(circuit_id,
                            dateStart=dt.datetime(2011,4,1),
                            dateEnd=dt.datetime(2011,5,1),
                            method='max',
                            requireMonotonic=True,
                            monotonicThreshold=-1,
                            reportThreshold=12,
                            verbose=0):
    date = dateStart
    i = 0.0
    energyAccumulator = 0.0
    while date <= dateEnd:
        tempData = getDailyEnergyForCircuit(circuit_id, date, verbose=verbose,
                                                              method='max',
                                                              requireMonotonic=requireMonotonic,
                                                              monotonicThreshold=monotonicThreshold,
                                                              reportThreshold=reportThreshold)
        if verbose > 0:
            print date, tempData
        if tempData > 0:
            energyAccumulator += tempData
            i += 1
        date += dt.timedelta(days=1)

    if i > 0:
        return energyAccumulator / i, i
    else:
        return 0, 0

'''
given a meter and a date range, returns a numpy array of energy consumption and two lists.
the lists represent the circuits and dates for the rows and columns of the array.
'''
def calculateTableOfConsumption(meter_id,
                                dateStart=dt.datetime(2011,5,12),
                                dateEnd = dt.datetime(2011,5,16),
                                strict=True):
    circuit_id = getCircuitsForMeter(meter_id)
    # define numpy array for data
    numRows = (dateEnd - dateStart).days + 1
    numColumns = len(circuit_id)
    data = np.zeros((numRows, numColumns))

    dates = []
    date = dateStart
    i = 0
    while date <= dateEnd:
        dates.append(date)
        j = 0
        for cid in circuit_id:
             data[i,j] = getDailyEnergyForCircuit(cid,
                                                  date,
                                                  verbose=0,
                                                  method='max',
                                                  requireMonotonic=True,
                                                  reportThreshold=12,
                                                  monotonicThreshold=-1,
                                                  strict=strict)
             j += 1
        date += dt.timedelta(days=1)
        i += 1

    return dates, circuit_id, data

'''
for a meter and daterange, outputs a table of percentage of time that greater
than zero credit is in the account.
'''
def calculateTimeWithCredit(meter_id,
                            dateStart=dt.datetime(2011,4,1),
                            dateEnd = dt.datetime(2011,5,1)):
    circuit_id = getCircuitsForMeter(meter_id)
    print ' '.ljust(10),
    for cid in circuit_id:
        print str(cid).rjust(6),
    print
    print '% credit'.ljust(10),
    for cid in circuit_id:
        dates, credit = getDataListForCircuit(cid, dateStart, dateEnd, quantity='credit')
        credit = np.array(credit)
        hoursWithCredit = len(np.extract(credit > 0, credit))
        totalHours = len(credit)
        timeWithCredit = float(hoursWithCredit) / float(totalHours)
        print ('%0.2f' % timeWithCredit).rjust(6),
    print

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
        if log.watthours > 0 and log.credit <= 0:
            logList.append((log.date, log.circuit_id, log.watthours))
    logList = list(set(logList))
    logList.sort()

    cw = 20
    print 'date'.rjust(cw),
    print 'circuit id'.rjust(cw),
    print 'watthours'.rjust(cw)
    for log in logList:
        for l in log:
            print str(l).rjust(cw),
        print


if __name__ == "__main__":
    pass
    #getDataListForCircuit(91,verbose=2)





# for   inclusion in gateway:
# todo: pass meter id
def plotByTimeSeries(report, dates):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    for i, meter_id in enumerate([4,7,8]):
        meterCircuits = session.query(Circuit).filter(Circuit.meter_id == meter_id)
        meterName = session.query(Meter).filter(Meter.id == meter_id)[0].name
        print 'generating for ', meterName

        meterCircuits = [mc.id for mc in meterCircuits]
        meterCircuits.sort()
        print meterCircuits

        meterReport = report[:,meterCircuits]

        import matplotlib.pyplot as plt
        import matplotlib.dates
        messagesReceived = meterReport.sum(1)
        mpldates = matplotlib.dates.date2num(dates)

        ax = fig.add_subplot(3,1,i)
        ax.plot_date(mpldates,messagesReceived,'-x')
        ax.set_title(meterName)
        ax.set_xlabel('Date')
        ax.set_ylabel('# Reporting')
    fig.autofmt_xdate()
    fig.savefig('uptime_by_date_.pdf')
    plt.close()

