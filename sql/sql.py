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

def tf1(date=dt.datetime(2011,5,12), verbose=2):
    for c in range(1,100):
        print 'circuit', c
        wh = getWattHourListForCircuit(c, date)
        for w in wh:
            print w

def tf3(dateStart=dt.datetime(2011,5,1),
                  dateEnd=dt.datetime(2011,5,13),
                  verbose=2):
    clist = range(13,99)
    clist = [25,57,70,74,77]
    for c in clist:
        print 'circuit', c
        wh = getDailyEnergyForCircuit(c, dateStart, verbose)
        print wh
        plotWattHoursForCircuit(c, dateStart, dateEnd)

def tf4():
    plotWattHoursForAllCircuitsOnMeter((4,7,8))
    printTableOfConsumption(4, strict=False)
    printTableOfConsumption(8, strict=False)

def tf5():
    print 'mali001'
    for cid in mali001:
        avg, N = calculateAverageEnergyForCircuit(cid, dt.datetime(2011,4,1),
                                                           dt.datetime(2011,5,18))
        print cid, ('%0.2f' % avg).rjust(8),\
                   ('%0.2f' % (avg*30*0.005)).rjust(8),\
                   str(N).rjust(8)
    print 'ml05'
    for cid in ml05:
        avg, N = calculateAverageEnergyForCircuit(cid, dt.datetime(2011,4,1),
                                                           dt.datetime(2011,5,18))
        print cid, ('%0.2f' % avg).rjust(8),\
                   ('%0.2f' % (avg*30*0.005)).rjust(8),\
                   str(N).rjust(8)
    print 'ml06'
    for cid in ml06:
        avg, N = calculateAverageEnergyForCircuit(cid, dt.datetime(2011,4,1),
                                                           dt.datetime(2011,5,18))
        print cid, ('%0.2f' % avg).rjust(8),\
                   ('%0.2f' % (avg*30*0.005)).rjust(8),\
                   str(N).rjust(8)

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

'''
returns plot axis with data from circuit
'''
def plotWattHoursForCircuit(circuit_id,
                            dateStart=dt.datetime(2011,5,12),
                            dateEnd=dt.datetime(2011,5,13)):
    dates, watthours = getWattHourListForCircuit(circuit_id, dateStart, dateEnd)
    dates = matplotlib.dates.date2num(dates)
    fig = plt.figure()
    ax = fig.add_axes((.2,.2,.6,.6))
    ax.plot_date(dates, watthours, 'x-')
    titleString = 'circuit ' + str(circuit_id) + ' watthours'
    ax.set_title(titleString)

    return ax

'''
plots all watthour readings for a meter on a grid over a given date range
'''
def plotWattHoursForAllCircuitsOnMeter(meter_id,
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
            fig, ax = plt.subplots(4, 5, sharex = True, figsize=(11,8.5))
            stride = 4
        else:
            fig, ax = plt.subplots(4, 3, sharex = True, figsize=(10,8))
            stride = 4

        for i,c in enumerate(circuits):
            dates, watthours = getWattHourListForCircuit(c, dateStart, dateEnd)
            dates = matplotlib.dates.date2num(dates)
            titleString = 'circuit ' + str(c) + ' watthours'
            thisAxes = ax[i % stride, i / stride]
            thisAxes.plot_date(dates, watthours, ls='-', ms=3, marker='o', mfc=None)
            #thisAxes.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=(0)))
            #thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
            thisAxes.text(0.7,0.7,str(c),transform = thisAxes.transAxes)
            if max(watthours) < 50:
                thisAxes.set_ylim((0,50))
            else:
                thisAxes.set_ylim((0,150))
            #ax[i].set_yticks((0,50,100))
            #ax[i].set_title(titleString)
            #ax[i].grid(True)

        fileNameString = 'meter' + str(mid) + '.pdf'
        fig.suptitle(fileNameString)
        fig.autofmt_xdate()
        fig.savefig(fileNameString)

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
'''
plot credit or watthours for all circuits on a meter
'''
def plotForAllCircuitsOnMeter(meter_id,
                              dateStart=dt.datetime(2011,5,13),
                              dateEnd=dt.datetime(2011,5,18),
                              quantity='credit',
                              showMains=False):

    circuits = getCircuitsForMeter(meter_id)

    # drop mains circuit
    if showMains == False:
        for c in circuits:
            if session.query(Circuit).filter(Circuit.id == c)[0].ip_address == '192.168.1.200':
                circuits.remove(c)

    #fig, ax = plt.subplots(len(circuits), 1, sharex = True, figsize=(5,15))
    if len(circuits) > 12:
        fig, ax = plt.subplots(4, 5, sharex = True, figsize=(11,8.5))
        stride = 4
    else:
        fig, ax = plt.subplots(4, 3, sharex = True, figsize=(10,8))
        stride = 4

    for i,c in enumerate(circuits):
        if quantity == 'credit':
            dates, data = getCreditListForCircuit(c, dateStart, dateEnd)

        dates = matplotlib.dates.date2num(dates)
        titleString = 'circuit ' + str(c) + ' watthours'
        thisAxes = ax[i % stride, i / stride]
        thisAxes.plot_date(dates, data, ls='-', ms=3, marker='o', mfc=None)
        #thisAxes.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=(0)))
        #thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
        thisAxes.text(0.7,0.7,str(c),transform = thisAxes.transAxes)

    fileNameString = 'meter credit ' + str(meter_id) + '.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    fig.savefig(fileNameString)


# printing functions

'''
prints a table of whether or not circuits have reported on certain dates
'''
def printHugeMessageTable(startDate = dt.datetime(2011, 5, 1),
                          endDate   = dt.datetime(2011, 5, 13)):
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
for a given circuit_id and date, this function returns a list of
watthour readings and dates.  uses set() to remove duplicate entries.
input:
    circuit_id - circuit database id
    dateStart - datetime object for day of data.  data returned dateStart < date <= dateEnd
output:
    dates - date stamps for watthour array
    watthours - reported watthours
'''
def getWattHourListForCircuit(circuit_id,
                              dateStart=dt.datetime(2011,5,12),
                              dateEnd=dt.datetime(2011,5,13),
                              verbose=0):
    # get query based on circuit and date
    logs = session.query(PrimaryLog)\
                  .filter(PrimaryLog.circuit_id == circuit_id)\
                  .filter(PrimaryLog.date > dateStart)\
                  .filter(PrimaryLog.date <= dateEnd)\
                  .order_by(PrimaryLog.date)

    # turn query into a sorted list of unique dates and watthour readings
    data = [(l.date, l.watthours) for l in logs]
    data = list(set(data))
    data.sort()
    dates = [d[0] for d in data]
    watthours = [d[1] for d in data]

    # send details to console if requested
    if verbose >= 1:
        for i in range(len(dates)):
            print dates[i],watthours[i]

    return dates, watthours

'''
for a given circuit_id and date, this function returns a list of
credit readings and dates.  uses set() to remove duplicate entries.
input:
    circuit_id - circuit database id
    dateStart - datetime object for day of data.  data returned dateStart < date <= dateEnd
output:
    dates - date stamps for watthour array
    credit - reported watthours
'''
def getCreditListForCircuit(circuit_id,
                              dateStart=dt.datetime(2011,5,12),
                              dateEnd=dt.datetime(2011,5,13),
                              verbose=0):
    # get query based on circuit and date
    logs = session.query(PrimaryLog)\
                  .filter(PrimaryLog.circuit_id == circuit_id)\
                  .filter(PrimaryLog.date > dateStart)\
                  .filter(PrimaryLog.date <= dateEnd)\
                  .order_by(PrimaryLog.date)

    # turn query into a sorted list of unique dates and watthour readings
    data = [(l.date, l.credit) for l in logs]
    data = list(set(data))
    data.sort()
    dates = [d[0] for d in data]
    credit = [d[1] for d in data]

    # send details to console if requested
    if verbose >= 1:
        for i in range(len(dates)):
            print dates[i],watthours[i]

    return dates, credit

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

    dates, watthours = getWattHourListForCircuit(circuit_id, dateStart, dateEnd, verbose)
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
        dates, credit = getCreditListForCircuit(cid, dateStart, dateEnd)
        credit = np.array(credit)
        hoursWithCredit = len(np.extract(credit>0, credit))
        totalHours = len(credit)
        timeWithCredit = float(hoursWithCredit)/float(totalHours)
        print ('%0.2f' % timeWithCredit).rjust(6),
    print


# deprecated or unpopular functions

'''
deprecated function
this function takes a circuit_id and the start and end date and outputs the energy
based on the 23:59:59 reporting.
input:
    circuit_id  database id for a circuit
    startDate   datetime object
    endDate     datetime object
    verbose     int, higher for more detail, zero for none
output:
    text dump to console
'''
def analyzeDailyEnergyPerCircuit(circuit_id, startDate, endDate, verbose = 0):
    # get logs based on circuit
    logs = session.query(PrimaryLog).filter(PrimaryLog.circuit_id == circuit_id)
    # filter according to date
    logs = logs.filter(PrimaryLog.date > startDate).filter(PrimaryLog.date < endDate)
    # analyze only the reports at 23:59:59
    data = np.array([l.watthours for l in logs if (l.date.hour == 23)
                                              and (l.date.minute == 59)
                                              and (l.date.second == 59)])
    widths = (3, 10, 10, 10, 10, 10, 5)
    if data.shape[0] == 0:
        print 'no data for circuit', circuit_id
    else:
        printTableRow((str(circuit_id),
                       '%0.2f' % data.min(),
                       '%0.2f' % data.mean(),
                       '%0.2f' % data.max(),
                       '%0.2f' % data.std(),
                       '%0.2f' % (data.std()/data.mean()),
                       str(data.shape[0])),
                       widths)
    if verbose > 0:
        for l in logs:
            if l.date.hour == 23 and l.date.minute == 59 and l.date.second == 59:
                print l.date, l.watthours

'''
this function takes a tuple of ints as an argument and outputs a text table
of watt hour information from the 23:59:59 reports by calling
analyzeDailyEnergyPerCircuit.
input:
    meter_id  tuple of ints
output:
    text dump to console
'''
def meterAnalyze(meter_id, verbose=0):
    import datetime as dt
    startDate = dt.datetime(2011,3,25)
    endDate = dt.datetime(2011,4,26)
    for mid in meter_id:
        # get list of circuits associated with meter
        circuits = session.query(Circuit).filter(Circuit.meter_id == mid).order_by(Circuit.id)
        circuits = [c.id for c in circuits]
        # print out header for table
        print
        print 'watt hour data for meter', mid
        print 'over date range', startDate, 'to', endDate
        widths = (3, 10, 10, 10, 10, 10, 5)
        printTableRow(('cid', 'min', 'mean', 'max', 'std', 'std/mean', 'N'), widths)
        # iterate over circuits and call analyzeDailyEnergyPerCircuit
        for c in circuits:
            analyzeDailyEnergyPerCircuit(c, startDate, endDate, verbose=verbose)

'''
creates a table of 1/0 values for whether or not a circuit reported at
the associated time
output:
    report = date by circuit numpy array of 1 or 0 values for circuit reporting
    dates  = list of dates corresponding to rows of report array
'''
def generateReportArray(startDate = dt.datetime(2011, 5, 1),
                        endDate   = dt.datetime(2011, 5, 13)):
    import datetime as dt
    import numpy as np

    circuit = session.query(Circuit).order_by(Circuit.id).all()
    clist = [c.id for c in circuit]
    #clist.sort()

    # report array size
    numCol = max(clist) + 1
    numRow = (endDate - startDate).days * 24
    report = np.zeros((numRow, numCol))

    # initialize date list
    dates = []
    originalQuery = session.query(PrimaryLog)

    start = startDate
    i = 0
    while 1:
        end = start + dt.timedelta(hours=1)
        thisQuery = originalQuery

        # this no longer deals with double report problem at 11pm
        # take reports in the hour between start and end
        thisQuery = thisQuery.filter(PrimaryLog.date >= start)\
                             .filter(PrimaryLog.date < end)
        #thisQuery = thisQuery.filter(PrimaryLog.date == endDate)
        cclist = [tq.circuit_id for tq in thisQuery]
        #cclist.sort()
        # add to numpy array
        report[i, cclist] = 1
        dates.append(start)
        i += 1

        start = start + dt.timedelta(hours=1)
        if start >= endDate:
            break
    return (report, dates)


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

if __name__ == "__main__":
    pass