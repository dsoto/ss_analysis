'''
'''

import os
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
verbose = 0

def getData(plotCircuit, plotDate, downsample):
    if verbose == 1:
        print 'getting data for', plotCircuit, plotDate
    data = []
    for dirname, dirnames, filenames in os.walk(plotDate):
        for filename in filenames:
            if plotCircuit in filename:
                if verbose ==1:
                    print 'getting data for', dirname
                tempData = np.loadtxt(dirname+'/'+filename, 
                                      delimiter=',', 
                                      usecols = range(19),
                                      skiprows = 1)
                # deal with case of one line file
                if data == []:
                    data = tempData
                    if data.shape == (19,):
                        data = data.reshape(1,19)
                elif tempData.shape == (19,):
                    tempData = tempData.reshape(1,19)
                else:
                    data = np.append(data, tempData, axis=0)
    # check for nonexistent data
    if data != []:
        index = range(0, data.shape[0], downsample)
        data = data[index]
                    
    return data

# create dictionary of header strings
def getHeaderStrings():
    headerString = 'Time Stamp,Credit,Watts,Volts,Amps,Watt Hours SC20,Watt Hours Today,Max Watts,Max Volts,Max Amps,Min Watts,Min Volts,Min Amps,Power Factor,Power Cycle,Frequency,Volt Amps,Relay Not Closed,Send Rate,Machine ID,Type'
    headers = headerString.split(',')
    d = {}
    for i,h in enumerate(headers):
        d[i]=h
    return d

plotColumnList = [1,2,6]
#plotColumnList = [5]
plotDateList = ['12/02','12/03','12/04','12/05','12/06','12/07','12/08','12/09']
#plotDateList = ['12/06']
plotCircuitList = ['201','202','203','204','205','206','207','208','209','210','211','212']
plotColorList  = ['b', 'r', 'g', 'k', 'b', 'r', 'g', 'k', 'b', 'r', 'g', 'k']
plotSymbolList  = ['x', 'x', 'x', 'x', 's', 's', 's', 's', 'd', 'd', 'd', 'd']
#plotCircuitList = ['201','202','203','205','206','207','209','210','211','212']
downsample = 100
d = getHeaderStrings()



# create circuits loop here
for plotColumn in plotColumnList:
    for plotDate in plotDateList:
        # figure is created for each column and date but for multiple circuits
        fig = plt.figure()
        axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))

        for i, plotCircuit in enumerate(plotCircuitList):
            # walk through files and generate temp file-like object
            data = getData(plotCircuit, plotDate, downsample)
            
            if data != []:
                # map time from float to int and then to string
                time = map(int, data[:,0])
                time = map(str, time)
                
                parsedDates = [dateutil.parser.parse(t) for t in time]
                
                # date2num returns a float number of seconds to represent date
                mplDates = matplotlib.dates.date2num(parsedDates)
                
                axis.plot_date(mplDates, data[:,plotColumn], 
                               marker = plotSymbolList[i], 
                               markeredgecolor = plotColorList[i], 
                               markerfacecolor = 'None',
                               label=plotCircuit)

            
        # figure out how to set range from midnight to midnight
        # figure out how to slant ticks
        # create data output text space on figure
        dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
        axis.xaxis.set_major_formatter(dateFormatter)
        fig.autofmt_xdate()
        axis.grid()
        axis.set_xlabel("time of day")
        axis.set_ylabel(d[plotColumn])
        axis.legend(loc=(1.0,0.0), title='Circuit', numpoints=1)
        plotFileName = plotDate[0:2] + plotDate[3:5] + '_' + d[plotColumn]
        print 'saving:', plotFileName
        fig.savefig(plotFileName + ".pdf")
        #plt.show()

