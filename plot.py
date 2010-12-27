'''
todo: 

make directory independent by hardcoding path to data files

fix so that you can plot mains 200 by putting proper formatting of columns

'''

import os
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
verbose = 0

numColumns = 20
dataDirectory = '/Users/dsoto/current/mali/logs/sd/2010'
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/2010'


def getData(plotCircuit, plotDate, downsample):
    if verbose == 1:
        print 'getting data for', plotCircuit, plotDate
    data = []
    directoryToWalk = dataDirectory + '/' + plotDate
    if verbose == 1:
        print directoryToWalk
    for dirname, dirnames, filenames in os.walk(directoryToWalk):
        if verbose == 1:
            print dirname, dirnames, filenames
        for filename in filenames:
            if plotCircuit in filename:
                if verbose == 1:
                    print 'getting data for', dirname
                # usecols = [crap] is a hideous hack to avoid text string column
                if verbose == 1:
                    print dirname + '/' + filename
                tempData = np.loadtxt(dirname+'/'+filename, 
                                      delimiter=',', 
                                      usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                                                 11, 12, 13, 14, 15, 16, 17, 18, 20],
                                      skiprows = 1)
                # deal with case of one line file
                if data == []:
                    data = tempData
                    if data.shape == (numColumns,):
                        data = data.reshape(1,numColumns)
                elif tempData.shape == (numColumns,):
                    tempData = tempData.reshape(1,numColumns)
                else:
                    data = np.append(data, tempData, axis=0)
    # check for nonexistent data
    if data != []:
        index = range(0, data.shape[0], downsample)
        data = data[index]
    if verbose == 1:
        print data
    return data

# create dictionary of header strings
def getHeaderStrings():
    d = {}
    headers = ['Time Stamp',
               'Watts',
               'Volts',
               'Amps',
               'Watt Hours SC20',
               'Watt Hours Today',
               'Max Watts',
               'Max Volts',
               'Max Amps',
               'Min Watts',
               'Min Volts',
               'Min Amps',
               'Power Factor',
               'Power Cycle',
               'Frequency',
               'Volt Amps',
               'Relay Not Closed',
               'Send Rate',
               'Machine ID',
               'Credit']
    for i,h in enumerate(headers):
        d[i]=h
    return d


plotColumnList = [1,2,5,6,19]
#plotColumnList = range(20)
plotDateList = ['12/25']
#plotDateList = ['12/06']
# currently you cannot plot MAINS 200
plotCircuitList = ['201','202','203','204','205','206','207','208','209','210','211','212']
#plotCircuitList = ['208']
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
        axis.set_title(plotDate + " " + d[plotColumn])
        axis.legend(loc=(1.0,0.0), title='Circuit', numpoints=1)
        plotFileName = plotDate[0:2] + plotDate[3:5] + '_' + d[plotColumn]
        print 'saving:', plotFileName
        fig.savefig(plotFileName + ".pdf")
        #plt.show()

