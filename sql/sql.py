# uses python 2.7.1
import sqlalchemy
import urllib
import numpy as np                # version 1.5.1
import matplotlib.dates           # version 1.0.1
import matplotlib.pyplot as plt   # version 1.0.1
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
#ml06 = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 96, 97, 98, 99, 100]
ml06 = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 96, 97]

today = dt.datetime.now()
dateEnd = dt.datetime(today.year, today.month, today.day) - dt.timedelta(days=1)
dateStart = dateEnd - dt.timedelta(days=6)
may_15 = dt.datetime(2011,5,15)
jun_15 = dt.datetime(2011,6,15)

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

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    _type = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': _type}
    uuid = Column(String)
    start = Column(DateTime)
    end = Column(String)
    state = Column(Boolean)
    circuit_id = Column(Integer, ForeignKey('circuit.id'))
    circuit = relation(Circuit,
                       cascade="all,delete",
                       lazy=False, primaryjoin=circuit_id == Circuit.id)

    def __init__(self, circuit=None, state=True):
        self.uuid = str(uuid.uuid4())
        self.start = get_now()
        self.circuit = circuit
        self.state = state

    def getMessage(self, session):
        if len(self.job_message) is not 0:
            incoming_uuid = self.job_message[0]
        elif len(self.kannel_job_message) is not 0:
            incoming_uuid = self.kannel_job_message[0].incoming
        return session.query(IncomingMessage).\
                            filter_by(uuid=incoming_uuid).first()

    def url(self):
        return "jobs/job/%s/" % self.id

    def toDict(self):
        return {"uuid": self.uuid,
                "state": self.state,
                "date": self.start,
                "type": self._type}

    def __str__(self):
        return "job"


class AddCredit(Job):
    __tablename__ = "addcredit"
    __mapper_args__ = {'polymorphic_identity': 'addcredit'}
    description = "This job adds energy credit to the remote circuit"
    id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)
    credit = Column(Integer)


    def __init__(self, credit=None, circuit=None):
        Job.__init__(self, circuit)
        self.credit = credit

    def __str__(self):
        return "job=cr&jobid=%s&cid=%s&amt=%s;" % (self.id,
                                                self.circuit.ip_address,
                                                float(self.credit))

class TurnOff(Job):
    __tablename__ = "turnoff"
    __mapper_args__ = {'polymorphic_identity': 'turnoff'}
    description = "This job turns off the circuit on the remote meter"
    id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)

    def __init__(self, circuit=None):
        Job.__init__(self, circuit)

    def __str__(self):
        return "job=coff&jobid=%s&cid=%s;" % (self.id, self.circuit.ip_address)


class TurnOn(Job):
    __tablename__ = "turnon"
    __mapper_args__ = {'polymorphic_identity': 'turnon'}
    description = "This job turns on the circuit off the remote meter"
    id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)

    def __init__(self, circuit=None):
        Job.__init__(self, circuit)

    def __str__(self):
        return "job=con&jobid=%s&cid=%s;" % (self.id, self.circuit.ip_address)


class Mping(Job):
    """ Job that allows the admin to 'ping' a meter"""
    __tablename__ = 'mping'
    __mapper_args__ = {'polymorphic_identity': 'mping'}
    description = "This job turns on the circuit off the remote meter"
    id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)

    def __init__(self, meter=None):
        Job.__init__(self, self.getMain(meter))

    def getMain(self, meter):
        return meter.get_circuits()[0]

    def __str__(self):
        return "job=mping&jobid=%s;" % self.id


class Cping(Job):
    """ Job that allows the admin to 'ping' a meter"""
    __tablename__ = 'cping'
    __mapper_args__ = {'polymorphic_identity': 'cping'}
    description = "This job turns on the circuit off the remote meter"
    id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)

    def __init__(self, circuit=None):
        Job.__init__(self, circuit)

    def __str__(self):
        return "job=cping&jobid=%s&cid=%s;" % (self.id,
                                               self.circuit.ip_address)


#--------------------------------------------------------------------------------------------#
# convenience and helper functions

def printJobs():
    #jobs = session.query(Job).filter(Job.circuit_id == 14)
    jobs = session.query(Job).filter(Job._type == 'addcredit').filter(Job.circuit_id ==14)
    for j in jobs:
        print j

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


#--------------------------------------------------------------------------------------------#
# plotting functions

def plotDatasForCircuit(circuit_id,
                        dateStart=dt.datetime(2011,5,12),
                        dateEnd=dt.datetime(2011,5,13),
                        quantity=('watthours','credit'),
                        introspect=False):
    # set subplots for length of quantity
    numPlotsX = 1
    numPlotsY = len(quantity)

    # plot creation
    fig = plt.figure()

    # iterate through quantity
    for i,q in enumerate(quantity):
        dates, data = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity=q)
        dates = matplotlib.dates.date2num(dates)
        thisAxes = fig.add_subplot(numPlotsY, numPlotsX, i+1)
        thisAxes.plot_date(dates, data, ls='-', c='#eeeeee', ms=3, marker='o', mfc=None)
        thisAxes.set_title(q)
        thisAxes.grid(linestyle='-', color='#eeeeee')

    fig.autofmt_xdate()
    titleString = 'circuit ' + str(circuit_id) + ' multiple'
    if introspect:
        plt.show()
    fig.savefig(titleString + '.pdf')

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
    if introspect:
        plt.show()
    fig.savefig(titleString + '.pdf')

def plotPowerForCircuit(circuit_id,
                        dateStart=dateStart,
                        dateEnd=dateEnd,
                        introspect=True):
    dates, data = calculatePowerListForCircuit(circuit_id, dateStart, dateEnd)

    dates = matplotlib.dates.date2num(dates)
    fig = plt.figure()
    ax = fig.add_axes((.2,.2,.6,.6))
    ax.plot_date(dates, data, 'x-')
    titleString = 'circuit ' + str(circuit_id)
    ax.set_title(titleString)
    ax.set_ylabel("Power (W)")
    ax.set_xlabel("Time")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(titleString + '.pdf')


def plotDataForCircuitList(circuit_id_list,
                           dateStart=dateStart,
                           dateEnd=dateEnd,
                           quantity='credit',
                           introspect=False):
    '''
    this function takes a list of circuit ids and plots a grid of data for the
    specified quantity over the specified date range
    '''
    pass


'''
plot credit or watthours for all circuits on a meter
'''
def plotDataForAllCircuitsOnMeter(meter_id,
                              dateStart=dateStart,
                              dateEnd=dateEnd,
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
    plt.subplots_adjust(wspace=0.5)

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
        thisAxes.plot_date(dates, data, ls='-', c='#eeeeee', ms=3, marker='o', mfc=None)
        thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
        thisAxes.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(minticks=3,maxticks=5))
        thisAxes.text(0.7,0.7,str(c),transform = thisAxes.transAxes)

    fileNameString = 'meter ' + quantity + ' ' + str(meter_id) + '.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    if introspect:
        plt.show()
    fig.savefig(fileNameString)


#--------------------------------------------------------------------------------------------#
# printing functions

'''
prints a table of whether or not circuits have reported on certain dates
'''
def printHugeMessageTable(startDate=dateStart,
                          endDate=dateEnd):

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



# uncategorized functions

def removeDuplicates(dates, created, data):
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
    return dates, data

def inspectDayOfWatthours(circuit_id,
                          day=dt.datetime(2011,5,28),
                          verbose=0):
    dates, created, data = getRawDataListForCircuit(circuit_id,
                                                    day,
                                                    day + dt.timedelta(days=1),
                                                    quantity='watthours')
    print 'number of raw samples = ', len(dates)
    dates, data = removeDuplicates(dates, created, data)
    print 'number of samples after duplicate removal = ', len(dates)

    data = np.array(data)
    power = np.diff(data)
    dates = np.array(dates)

    # mask values with decrease in watthours and adjust for by one offset
    decreaseMask = power < 0
    np.insert(decreaseMask, 0, False)

    print 'decrease in watthours observed at these', sum(decreaseMask), 'times'
    print dates[decreaseMask]

    print 'apparent power consumption for day using max = ', max(data)

    '''
    print power
    print dates
    print data
    '''

def getDataListForCircuit(circuit_id,
                              dateStart=dateStart,
                              dateEnd=dateEnd,
                              quantity='watthours',
                              verbose=0):
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
    # get numpy arrays of dates, timestamps, and data
    dates, created, data = getRawDataListForCircuit(circuit_id,
                                                    dateStart,
                                                    dateEnd,
                                                    quantity,
                                                    verbose)
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

def getRawDataListForCircuit(circuit_id,
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
                  .order_by(PrimaryLog.date)

    # create separate arrays for each of these quantities
    dates = np.array([l.date for l in logs])
    data  = np.array([getattr(l, quantity) for l in logs])
    created = np.array([l.created for l in logs])

    return dates, created, data


def calculatePowerListForCircuit(circuit_id,
                                       dateStart=dateStart,
                                       dateEnd=dateEnd):
    '''
    pulls watthour data list and creates a report of the power consumed over that hour
    '''
    dates, data = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity='watthours')
    #print dates, data
    power_dates = []
    power_data = []
    for i in range(len(dates)):
        # if 1am energy sample is energy over last hour
        if dates[i].hour == 1:
            power_dates.append(dates[i])
            power_data.append(data[i])
        # only append if not 1am, after the first sample and if power is positive
        if (dates[i].hour != 1) and (i > 0) and ((dates[i] - dates[i-1]) == dt.timedelta(hours=1)):
            if (data[i] - data[i-1]) >= 0:
                power_dates.append(dates[i])
                power_data.append(data[i] - data[i-1])
    #print power_dates
    #print power_data
    return power_dates, power_data

def printEnergyGridForCircuits(circuit_id_list,
                        dateStart = dateStart,
                        dateEnd = dateEnd):

    printTableRow(("circuit", "max", "mean", "min"),(4,20,20,20))

    for i,c in enumerate(circuit_id_list):
        # grab energy data for circuit
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        printTableRow((c,max(data),data.mean(),data.min()),(4,20,20,20))
        '''
        print c,
        print max(data),
        print data.mean(),
        print data.min()
        '''

def plotEnergyGridForCircuits(circuit_id_list,
                        dateStart = dateStart,
                        dateEnd = dateEnd):

    fig = plt.figure()
    # create figure and axes with subplots
    if len(circuit_id_list) > 12:
        numPlotsX = 4
        numPlotsY = 5
    else:
        numPlotsX = 4
        numPlotsY = 3
    #fig, axes = plt.subplots(numPlotsY, numPlotsX, sharex=True)

    plt.subplots_adjust(wspace=0.5)

    # loop through circuits, get data, plot
    for i,c in enumerate(circuit_id_list):
        # grab energy data for circuit
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        print c, max(data), data.mean(), data.min()
        dates = matplotlib.dates.date2num(dates)

        thisAxes = fig.add_subplot(numPlotsX, numPlotsY, i+1)
        #thisAxes = axes[i/numPlotsY, i%numPlotsX]
        thisAxes.plot_date(dates, data, ls='-', ms=3, marker='o', mfc=None)
        thisAxes.set_ylim((0,50))
        #thisAxes.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=(0)))
        thisAxes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
        thisAxes.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(minticks=3,maxticks=5))
        thisAxes.text(0.5,0.7,str(c),transform = thisAxes.transAxes)

    fileNameString = 'testenergyplotgrid.pdf'
    fig.suptitle(fileNameString)
    fig.autofmt_xdate()
    #if introspect:
    #    plt.show()
    fig.savefig(fileNameString)

def plotAveragedPowerForCircuit(circuit_id,
                                dateStart=dateStart,
                                dateEnd=dateEnd,
                                plotFileName='averagePower.pdf'):
    # get list for entire date range
    dates, data = calculatePowerListForCircuit(circuit_id, dateStart=dateStart, dateEnd=dateEnd)

    # create dictionary with key = hour and value = []
    dataDict = {}
    for hour in range(0,24):
        dataDict[hour] = []

    # iterate over list and place samples in a dictionary with key=hour
    for i, date in enumerate(dates):
        dataDict[date.hour].append(data[i])

    # iterate over keys and average watthour readings for each hour

    # plot both of these

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.1, 0.8, 0.8))
    for key in dataDict.keys():
        # construct a list of hours the same length as dictionary list
        hour = key * np.ones(len(dataDict[key]))
        ax.plot(hour, dataDict[key],'o', mfc='#dddddd', mec='#dddddd')
        avg_energy_for_hour = np.array(dataDict[key]).mean()
        ax.plot(key, avg_energy_for_hour, 'kx', ms=10)
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Average Power (Watts)')
    fig.savefig(plotFileName)

def plotAveragedAccumulatedHourlyEnergyForCircuit(circuit_id,
                                                  dateStart=dateStart,
                                                  dateEnd=dateEnd,
                                                  plotFileName = 'averagedAccumulatedEnergy.pdf'):
    '''
    plots averaged consumption for a single circuit
    report on the hour reports consumption for previous hour
    '''

    # get list for entire date range
    dates, data = getDataListForCircuit(circuit_id, dateStart=dateStart, dateEnd=dateEnd)

    # create dictionary with key = hour and value = []
    dataDict = {}
    for hour in range(0,24):
        dataDict[hour] = []

    # iterate over list and place samples in a dictionary with key=hour
    for i, date in enumerate(dates):
        dataDict[date.hour].append(data[i])

    # iterate over keys and average watthour readings for each hour

    # plot both of these

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.1, 0.8, 0.8))
    for key in dataDict.keys():
        # construct a list of hours the same length as dictionary list
        hour = key * np.ones(len(dataDict[key]))
        ax.plot(hour, dataDict[key],'o', mfc='#dddddd', mec='#dddddd')
        avg_energy_for_hour = np.array(dataDict[key]).mean()
        ax.plot(key, avg_energy_for_hour, 'kx', ms=10)
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Acumulated Energy (Watthours)')
    fig.savefig(plotFileName)

def getEnergyForCircuit(circuit_id,
                        dateStart=dateStart,
                        dateEnd=dateEnd):
    data = []
    dates = []
    currentDate = dateStart
    while currentDate < dateEnd:
        data.append(getEnergyForCircuitForDayByMax(circuit_id, currentDate))
        dates.append(currentDate)
        currentDate += dt.timedelta(days=1)
    data = np.array(data)
    return data, dates

def plotEnergyHistogram(circuit_id_list,
                        dateStart=dateStart,
                        dateEnd=dateEnd,
                        bins=10,
                        range=(0,200),
                        plotFileName='energyHistogram.pdf'):
    dataList = np.array([])
    for i,c in enumerate(circuit_id_list):
        # grab energy data for circuit
        data, dates = getEnergyForCircuit(c, dateStart, dateEnd)
        # append data onto master list of energy
        dataList = np.append(dataList, data)
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.1,0.8,0.8))
    ax.hist(dataList, bins=bins, range=range, normed=False, facecolor='#dddddd')
    ax.set_xlabel("Daily Watthours")
    ax.set_ylabel("Days of Usage")
    #plt.show()
    fig.savefig(plotFileName)

def getEnergyForCircuitForDayByMax(circuit_id,
                                   day=dt.datetime(2011,6,8)):
    dates, data = getDataListForCircuit(circuit_id, day, day+dt.timedelta(days=1))
    #print circuit_id, day
    #inspectDayOfWatthours(circuit_id, day, day+dt.timedelta(days=1))
    #print max(data)
    #print
    return max(data)


def energyTest(circuit_id_list, dateStart=dt.datetime(2011,6,5),
                           dateEnd=dt.datetime(2011,6,8)):

    for circuit_id in circuit_id_list:
        date = dateStart
        while date <= dateEnd:
            getEnergyForCircuitForDayByMax(circuit_id, date)
            date += dt.timedelta(days=1)


def calculateTimeWithCreditForCircuit(circuit_id,
                                      dateStart=dateStart,
                                      dateEnd=dateEnd):
    dates, credit = getDataListForCircuit(circuit_id, dateStart, dateEnd, quantity='credit')
    credit = np.array(credit)
    hoursWithCredit = len(np.extract(credit > 0, credit))
    totalHours = len(credit)
    timeWithCredit = float(hoursWithCredit) / float(totalHours)
    return timeWithCredit

def calculateTimeWithCreditForCircuitList(circuit_id_list,
                                          dateStart=dateStart,
                                          dateEnd=dateEnd):
    '''
    for a meter and daterange, outputs a table of percentage of time that greater
    than zero credit is in the account.
    '''
    print ' '.ljust(10),
    for cid in circuit_id_list:
        print str(cid).rjust(6),
    print
    print '% credit'.ljust(10),
    credit_list = []
    for cid in circuit_id_list:
        timeWithCredit = calculateTimeWithCreditForCircuit(cid, dateStart, dateEnd)
        credit_list.append(timeWithCredit)
        print ('%0.2f' % timeWithCredit).rjust(6),
    print
    return credit_list

def plotScatterCreditConsumedVsTimeWithCreditForCircuitList(circuit_id_list,
                                                            dateStart=dateStart,
                                                            dateEnd=dateEnd,
                                                            plotFileName='scatterCreditTime.pdf'):
    credit_consumed = printReportOfCreditConsumedForCircuitList(circuit_id_list, dateStart, dateEnd)
    time_with_credit = calculateTimeWithCreditForCircuitList(circuit_id_list, dateStart, dateEnd)
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.1,0.8,0.8))
    ax.plot(credit_consumed, time_with_credit, 'o', mfc='#cccccc')
    ax.set_xlabel('Monthly Electricity Expenditure')
    ax.set_ylabel('Fraction of Time with Credit Available')
    fig.savefig(plotFileName)


def calculateAverageTimeWithCreditForCircuitList(circuit_id_list,
                                                 dateStart=dateStart,
                                                 dateEnd=dateEnd):
    averageTime = 0
    numCircuits = len(circuit_id_list)
    for cid in circuit_id_list:
        timeWithCredit = calculateTimeWithCreditForCircuit(cid, dateStart, dateEnd)
        averageTime += timeWithCredit / numCircuits
    return averageTime

def plotHistogramTimeWithCreditForCircuitList(circuit_id_list,
                                              dateStart=dateStart,
                                              dateEnd=dateEnd,
                                              range=(0.0, 1.0),
                                              plotFileName='creditHistogram.pdf'):
    timeList = []
    for cid in circuit_id_list:
        timeWithCredit = calculateTimeWithCreditForCircuit(cid, dateStart, dateEnd)
        timeList.append(timeWithCredit)

    # plot histogram
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.1,0.8,0.8))
    hist, bin_edges = np.histogram(timeList, bins=10, range=range)
    ax.bar(bin_edges[:-1], hist, width=0.1, color='#dddddd')
    #ax.hist(timeList, bins=10, range=range, normed=False, cumulative=False, facecolor='#dddddd')
    ax.set_xlabel("Percentage of time with credit available")
    ax.set_ylabel("Customers")
    ax.set_xlim(range)
    fig.savefig(plotFileName)

def plotHistogramCreditConsumed(circuit_id_list,
                                dateStart=dateStart,
                                dateEnd=dateEnd,
                                plotFileName='consumptionHistogram.pdf'):

    consumptionList = printReportOfCreditConsumedForCircuitList(circuit_id_list, dateStart, dateEnd)

    range = (0,2500)
    bins = 10
    fig = plt.figure()
    ax = fig.add_axes((0.1,0.3,0.8,0.6))
    ax.hist(consumptionList, bins=10, range=range, normed=False, facecolor='#dddddd')
    #ax.hist(consumptionList)
    ax.set_xlabel("Monthly Credit Consumed (XFCA)")
    ax.set_ylabel("Customers")
    ax.set_xlim(range)
    annotation = []
    annotation.append('circuits = ' + str(circuit_id_list))
    annotation.append('date start = ' + str(dateStart))
    annotation.append('date end = ' + str(dateEnd))
    annotation = '\n'.join(annotation)
    import matplotlib.font_manager as mpf
    textFont = mpf.FontProperties()
    textFont.set_family('monospace')
    textFont.set_size(6)

    fig.text(0.01,0.01, annotation, fontproperties=textFont)
    fig.savefig(plotFileName)


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

# def getCreditPurchaseList():

# def getCreditPurchaseTotal():

# def

def calculateCreditConsumedForCircuit(circuit_id,
                            dateStart=dateStart,
                            dateEnd=dateEnd,
                            threshold = 100,
                            verbose=0):
    dates, data = getDataListForCircuit(circuit_id,
                            dateStart=dateStart,
                            dateEnd=dateEnd,
                            quantity='credit')
    credit_derivative = np.diff(data)
    # only calculate decreases
    credit_derivative = np.extract(credit_derivative < 0, credit_derivative)
    # invert credit derivative
    credit_derivative *= -1
    # ignore decreases greater than threshold
    credit_derivative = np.extract(credit_derivative < threshold, credit_derivative)
    credit_consumed = sum(credit_derivative)
    return credit_consumed

def printReportOfCreditConsumedForCircuitList(circuit_id_list,
                            dateStart=dateStart,
                            dateEnd=dateEnd,
                            threshold = 100,
                            verbose=0):
    list = []
    for cid in circuit_id_list:
         list.append(calculateCreditConsumedForCircuit(cid, dateStart, dateEnd, threshold=500))
    print list
    return list

def calculateCreditJumps(circuit_id,
                            dateStart=dt.datetime(2011,5,13),
                            dateEnd=dt.datetime(2011,6,13),
                            verbose=0):
    lowThreshold = 400

    dates, data = getDataListForCircuit(circuit_id,
                            dateStart=dt.datetime(2011,5,13),
                            dateEnd=dt.datetime(2011,6,13),
                            quantity='credit')
    dates = np.array(dates)
    data = np.array(data)
    diff = np.diff(data)
    mask = diff > 400
    np.delete(dates,0)
    #print diff[mask]
    #print dates[mask]

    if verbose > 0:
        for t in zip(diff[mask],dates[mask]):
            print circuit_id, str(t[0]).rjust(8), str(t[1]).rjust(21)

        print diff[mask].sum()
    return diff[mask].sum()

def calculateCreditPurchase(circuit_id,
                            dateStart=dt.datetime(2011,5,13),
                            dateEnd=dt.datetime(2011,6,13)):
    addCredit = session.query(AddCredit)\
                       .filter(Job.circuit_id == circuit_id)\
                       .filter(Job.start >= dateStart)\
                       .filter(Job.start <= dateEnd)\
                       .order_by(Job.start)

    sum = 0
    if verbose > 0:
        for ac in addCredit:
            sum += ac.credit
            print ac.id, ac.credit, ac.circuit_id, ac.start

    return sum

def printCreditPurchase(cid_list,
                       dateStart=dt.datetime(2011,6,1),
                       dateEnd=dt.datetime(2011,6,13)):
    for i, cid in enumerate(cid_list):
        sum = calculateCreditPurchase(cid, dateStart, dateEnd)
        print cid, sum


if __name__ == "__main__":
    pass
    #plotEnergyGridForCircuits(ml06, dt.datetime(2011,6,1), dt.datetime(2011,6,15))
    #printEnergyGridForCircuits(ml06, dt.datetime(2011,6,1), dt.datetime(2011,6,15))
    #plotEnergyHistogram(mali001, plotFileName="pelenganaHistogram.pdf")
    plotEnergyHistogram(ml06, dateStart=dt.datetime(2011,6,1), dateEnd=dt.datetime(2011,6,15),
                        bins=(0,1,5,10,15,20,25,30,35,40,45,50), plotFileName="ml06Histogram.pdf")
