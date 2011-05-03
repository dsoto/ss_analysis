'''
calls primaryParameters code to generate graphics for the
poster for IJCSD 2011
'''

import primaryParameters as pp
import datetime as dt

print('Begin Load Data')
d = pp.getDataAsRecordArray(downloadFile = False)
print('End Load Data\n')

dateStart = dt.datetime(2011,  3,  3)
dateEnd   = dt.datetime(2011,  5,  1)


# pelengana credit purchase table
pp.printRecharges(dateStart)

# pelengana energy daily average 14 charts
pp.plotWindowAveragedWatthoursByCircuit(d, dateStart, dateEnd)

# pelengana credit - use stacked
pp.plotCreditSeparateAxes(d, dateStart, dateEnd)

# pelengana energy for 2 months 14 charts
pp.plotTotalEnergyPerDayByCircuit(d, dateStart, dateEnd)

# bonus chart
pp.plotRecharges(dateStart)




