# plot primary parameter logs

import numpy as np
import dateutil.parser
import matplotlib.dates
import matplotlib.pyplot as plt

dataFileName = 'primaryParameters.csv'
usecols = [0,5,6,7,9]


d = np.loadtxt(dataFileName, delimiter=',', 
                             dtype=str, 
                             skiprows=1,
                             usecols=usecols)


for i,a in enumerate(d[:,3]):
    if a == 'None':
        d[i,3] = 0
 
circuits = set(d[:,1])
circuits.remove('25')

dataDict = {}
for c in circuits:
    dataDict[c] = []
    for a in d:
        if a[1]==c:
            dataDict[c].append(a)
            
for c in circuits:
    dataDict[c] = np.array(dataDict[c])
    
for c in circuits:
    dates = map(dateutil.parser.parse, dataDict[c][:,4])
    dates = matplotlib.dates.date2num(dates)
    credit = map(float, dataDict[c][:,3])
    wh = map(float, dataDict[c][:,0])
    
    sortIndices = dates.argsort()
    credit = np.take(credit, sortIndices)
    wh = np.take(wh, sortIndices)
    dates.sort()
    
    # limit by date range
    

#    plt.plot_date(dates, credit, '-', label=c)
    plt.plot_date(dates, wh, '-o', label=c)

plt.legend()
plt.show()

plt.savefig('primaryParameters.pdf')
