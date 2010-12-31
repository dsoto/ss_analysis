'''
script to plot out shared solar log data

configure type of plot by changing variables below
'''

plotColumnList = [1,2,5,6,19]
plotDateList = ['12/28','12/29']
plotCircuitList = ['200','201','202','203','204','205','206','207','208','209','210','211','212']


downsample = 100


import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
import ss_plotting as ssp

dataDirectory = '/Users/dsoto/current/mali/logs/sd/2010'
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/2010'

d = ssp.getHeaderStrings()

plotColorList  = ['k', 'b', 'r', 'g', 'k', 'b', 'r', 'g', 'k', 'b', 'r', 'g', 'k']
plotSymbolList  = ['o', 'x', 'x', 'x', 'x', 's', 's', 's', 's', 'd', 'd', 'd', 'd']



# create circuits loop here
for plotColumn in plotColumnList:
    for plotDate in plotDateList:
        # figure is created for each column and date but for multiple circuits
        fig = plt.figure()
        axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))

        for i, plotCircuit in enumerate(plotCircuitList):
            # check if trying to plot credit for MAINS otherwise it will fail
            if not ('200' in plotCircuit and plotColumn == 19):
                # walk through files and generate temp file-like object
                data = ssp.getData(plotCircuit, plotDate, downsample, dataDirectory)
            
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

