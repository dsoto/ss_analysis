from sql.analysis import *

import datetime as dt

wk_26 = dt.datetime(2011, 6, 27)
wk_27 = dt.datetime(2011, 7, 4)
wk_28 = dt.datetime(2011, 7, 11)
wk_29 = dt.datetime(2011, 7, 18)
wk_30 = dt.datetime(2011, 7, 25)


may_1 = dt.datetime(2011, 5, 1)
jun_1 = dt.datetime(2011, 6, 1)
jul_1 = dt.datetime(2011, 7, 1)
oct_1 = dt.datetime(2011, 10, 1)
oct_15 = dt.datetime(2011, 10, 15)
nov_1 = dt.datetime(2011, 11, 1)

tw.log.info('loading daniel.py')

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

def plot_watthours_credit_for_all_circuits(dateStart=dt.datetime(2011,6,25),
                              dateEnd=dt.datetime(2011,6,28)):
    '''
    prints a graph for each circuit available to be reviewed manually
    '''
    tw.log.info('running dailyReportForAllCircuits')
    tw.log.info('date start = ' + str(dateStart))
    tw.log.info('date end   = ' + str(dateEnd))

    # get a complete circuit list
    circuits = session.query(Circuit).order_by(Circuit.id)
    circuits = [c.id for c in circuits]

    for cid in circuits:
        tw.log.info('generating plot for circuit ' + str(cid))
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
                        dateStart=dt.datetime(2011, 7, 1),
                        dateEnd=dt.datetime(2011, 7, 4),
                        num_drop_threshold=1,
                        num_samples_threshold=16,
                        verbose=0):

    tw.log.info('entering plotSelfConsumption')

    meter = session.query(Meter).get(meter_id)
    mains_id = meter.getMainCircuit().id
    customer_circuit_list = [c.id for c in meter.getConsumerCircuits()]

    tw.log.info('mains circuit = ' + str(mains_id))
    tw.log.info('customer circuits = ' + str(customer_circuit_list))

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

        print current_date
        mains_energy = getEnergyForCircuitForDayByMax(mains_id, current_date)
        print 'mains energy =', mains_energy[0]

        total_energy = 0
        for cid in customer_circuit_list:

            customer_energy = getEnergyForCircuitForDayByMax(cid,
                                             current_date)
            #print customer_energy[0]
            total_energy += customer_energy[0]

        print 'total energy =', total_energy


        if mains_energy[1] > num_samples_threshold and mains_energy[2] < num_drop_threshold:
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

        current_date += dt.timedelta(days=1)

    dates = matplotlib.dates.date2num(dates)

    ax.plot_date(dates, household_consumption, label='Household Total')
    ax.plot_date(dates, mains_consumption, label='Meter Consumption')
    ax.legend()
    ax.set_ylim((0,2000))
    ax.set_xlim((matplotlib.dates.date2num(dateStart), matplotlib.dates.date2num(dateEnd)))
    fig.savefig('selfconsumption.pdf')
    tw.log.info('exiting plotSelfConsumption')

def generate_ictd_figures():
    print 'generating averagePower.pdf'
    plotAveragedPowerForCircuit(78, may_15, jun_15, plotFileName='ictd/averagePower.pdf')
    print 'generating consumptionHistogram.pdf'
    plotHistogramCreditConsumed(ml06, may_15, jun_15, plotFileName='ictd/consumptionHistogram.pdf')
    print 'creditHistogram.pdf'
    plotHistogramTimeWithCreditForCircuitList(ml05+ml06, may_15, jun_15, plotFileName='ictd/creditHistogram.pdf')
    print 'generating scatter.pdf'
    plotEnergyHistogram(ml06, dt.datetime(2011,6,1), jun_15, plotFileName='ictd/ml06Histogram.pdf')
    print 'generating energy histogram'
    plotScatterCreditConsumedVsTimeWithCreditForCircuitList(ml06, may_15, jun_15, plotFileName='ictd/scatterCreditHistogram.pdf')


if __name__ == "__main__":
    tw.log.info('entering __main__ of daniel.py')
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


    calculateSelfConsumption(6,
                             dateStart=dt.datetime(2011,7,13),
                             dateEnd=dt.datetime(2011,7,14))

    '''
    calculateSelfConsumption(7,
                             dateStart=dt.datetime(2011,6,1),
                             dateEnd=dt.datetime(2011,6,28),
                             num_samples_threshold=16,
                             verbose=1)
    '''
    #plotSelfConsumption()
    #dailyReportForAllCircuits(dt.datetime(2011, 6, 4), dt.datetime(2011, 6, 11))
    #plotEnergyHistogram(mali001,
    #                     dt.datetime(2011,6,1),
    #                     jun_15, bins=[0,1]+range(5,105,5), plotFileName='ictd/ml01Histogram.pdf')
    #plotHistogramCreditConsumed(mali001, may_15, jun_15,
    #                            bins = range(0, 21, 2), plotFileName='ictd/ml01_consumptionHistogram.pdf')

    tw.log.info('exiting __main__ of daniel.py')