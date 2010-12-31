verbose = 0
import os
import numpy as np
numColumns = 20


def getData(plotCircuit, plotDate, downsample, dataDirectory):
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
                if '200' in plotCircuit:
                    usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                               11, 12, 13, 14, 15, 16, 17, 18]
                else:                        
                     usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                                11, 12, 13, 14, 15, 16, 17, 18, 20]
                tempData = np.loadtxt(dirname+'/'+filename, 
                                      usecols = usecols,
                                      delimiter=',', 
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
