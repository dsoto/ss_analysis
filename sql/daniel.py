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

def dailyReportForAllCircuits(dateStart=dt.datetime(2011,6,25),
                              dateEnd=dt.datetime(2011,6,28)):
    '''
    prints a graph for each circuit available to be reviewed manually
    '''

    # get yesterdays date
    # this is bad, specify date soon
    #date = dt.datetime.now()
    #date = dt.datetime(date.year, date.month, date.day) - dt.timedelta(days=1)
    print dateStart, dateEnd

    # get a complete circuit list
    circuits = session.query(Circuit).order_by(Circuit.id)
    circuits = [c.id for c in circuits]

    print circuits

    #circuits = circuits[0:3]

    #plotDatasForCircuit(70, date, date+dt.timedelta(days=1), introspect=True)

    for cid in circuits:
        plotDatasForCircuit(cid,
                            dateStart,
                            dateEnd,
                            titleString=str(cid))

def calculateSelfConsumption(meter_id,
                             dateStart=dt.datetime(2011, 6, 1),
                             dateEnd=dt.datetime(2011, 7, 1),
                             num_samples_threshold=16,
                             verbose=0):
    circuit_list = getCircuitsForMeter(meter_id)

    total_energy = 0
    for cid in circuit_list:

        average_energy = calculateAverageEnergyForCircuit(cid,
                                         dateStart, dateEnd, verbose=verbose)
        print average_energy
        total_energy += average_energy
    print 'total energy =', total_energy

def plotSelfConsumption(meter_id=8,
                        dateStart=dt.datetime(2011, 6, 1),
                        dateEnd=dt.datetime(2011, 7, 4),
                        num_samples_threshold=16,
                        verbose=0):

    meter = session.query(Meter).get(meter_id)

    mains_id = meter.getMainCircuit().id

    customer_circuit_list = [c.id for c in meter.getConsumerCircuits()]

    print mains_id
    print customer_circuit_list


    # loop through days
    # for each day total household consumption and infer mains consumption
    # create list of dates, household consumption and mains consumption
    dates = []
    household_consumption = []
    mains_consumption = []

    fig = plt.figure()
    ax = fig.add_axes((0.1,0.1,0.8,0.8))

    current_date = dateStart
    while current_date < dateEnd:

        dates.append(current_date)

        print current_date,
        mains_energy = getEnergyForCircuitForDayByMax(mains_id, current_date)
        print mains_energy[0]

        total_energy = 0
        for cid in customer_circuit_list:

            customer_energy = getEnergyForCircuitForDayByMax(cid,
                                             current_date)
            print customer_energy[0]
            total_energy += customer_energy[0]

        print 'total energy =', total_energy

        mains_consumption.append(mains_energy[0] - total_energy)
        household_consumption.append(total_energy)

        current_date += dt.timedelta(days=1)

    dates = matplotlib.dates.date2num(dates)

    ax.plot_date(dates, household_consumption)
    ax.plot_date(dates, mains_consumption)
    ax.set_ylim((0,2000))
    plt.show()





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

    '''
    calculateSelfConsumption(6,
                             dateStart=dt.datetime(2011,6,24),
                             dateEnd=dt.datetime(2011,6,28))


    calculateSelfConsumption(7,
                             dateStart=dt.datetime(2011,6,1),
                             dateEnd=dt.datetime(2011,6,28),
                             num_samples_threshold=16,
                             verbose=1)
    '''
    plotSelfConsumption()