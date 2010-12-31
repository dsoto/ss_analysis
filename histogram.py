# script to plot histogram of power consumption

import ss_plotting as ssp
import numpy as np
import matplotlib.pyplot as plt

plotDateList = ['12/27']
plotCircuitList = ['201','202','203','204','205','206','207','208','209','210','211','212']
plotCircuitList = ['200']
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/2010'
downsample = 1
pmax = 300

for plotCircuit in plotCircuitList:
    for plotDate in plotDateList:

        data = ssp.getData(plotCircuit, plotDate, downsample, dataDirectory)

        if data !=[]:
            fig = plt.figure()
            axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))
            
            # each sample represents 3 seconds and we convert to hours
            weights = np.ones(len(data[:,1]))*3/60/60
            axis.hist(data[:,1], bins=pmax, range=(0,pmax),weights=weights)
            axis.set_title(plotCircuit)
    
            axis.set_xlabel('Power Consumed (W)')
            axis.set_ylabel('Time Used (hours)')
            #axis.set_ylim((0,6))
            plotTitle = plotDate + ' ' + plotCircuit
            axis.set_title(plotTitle)
            # print out figure with filename constructed from circuit and date
            # histogram_yyyymmdd_cid.pdf
            plotFileName = 'histogram_'
            plotFileName += '2010' + plotDate[0:2] + plotDate[3:5] + '_'
            plotFileName += plotCircuit + '.pdf'
            print 'writing', plotFileName
            fig.savefig(plotFileName)







