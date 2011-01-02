'''
Power Histogram:
This would be a histogram of all the non-zero watt readings for
customers (no mains, just individual circuits).  What is the typical
instantaneous power level (don't include zero power, only >0)?  Are
consumers typically running loads at about 10 watts, 100 watts, or ?  Is
this histogram skewed - what does that tell us?

For the watts histogram, is it possible to combine the data from all 12
circuits from all days in december into 1 histogram?  And to for the
X-axis to stay as is, but for the y-axis to be the overall percentage of
time for which the various power levels occurred (so just 0 to 1.0),
instead of hours on the y-axis?

loop through all dates and circuits
create one huge array of watt readings
plot normalized histogram
'''

import ss_plotting as ssp
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import datetime

dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'
plotCircuitList = ['201','202','203','205','206','207','208','209','210','211','212']
dateStart = datetime.datetime(2010, 12, 17)
dateEnd = datetime.datetime(2010, 12, 27)

data = []

for plotCircuit in plotCircuitList:
    print 'getting data for circuit ' + plotCircuit
    newData = ssp.getFormattedData(plotCircuit, dateStart, dateEnd, 1, dataDirectory)

    # append to large data array
    if data == []:
        data = newData
    else:
        data = np.append(data, newData, axis=0)

    print data.shape
    

pmax = 100
fig = plt.figure()
axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
axis.hist(data['Watts'], bins=pmax, range=(0,pmax), normed=True)
axis.set_title('Histogram')
axis.set_xlabel('Power Consumed (W)')
axis.set_ylabel('Frequency (arb)')
#axis.set_ylim((0,6))
fig.savefig('histogram_total.pdf')
