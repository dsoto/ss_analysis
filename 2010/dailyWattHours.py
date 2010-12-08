
import os    
import numpy as np

verbose = 1

outputFileList = []
outputFileDict = {}

# generate list of log files and find last hour of logging
for dirname, dirnames, filenames in os.walk('12/01'):
    if verbose == 1:
        print
        print dirname
        print dirnames
        print filenames
    if filenames == []:
        if verbose == 1:
            print 'no files in this directory'
    else:
        for filename in filenames:
            if filename not in outputFileList:
                outputFileList.append(filename)
            outputFileDict[filename] = dirname

# sort keys and output information
keys = outputFileDict.keys()
keys.sort()

for key in keys:
    print
    print key, outputFileDict[key]
    
    # open file in appropriate directory and pull last line
    filename = outputFileDict[key] + '/' + key

    # get appropriate column of data
    totalWattHourCol = 6
    # watch out for pesky mains file '200'
    if '200' in key:
        totalWattHourCol = 5
    data = np.loadtxt(filename, delimiter=',', 
                                usecols = (0,totalWattHourCol), 
                                skiprows=1)
    # some of these log files only have one line of data
    if data.shape == (2,):
        print int(data[0])
        print data[1], 'watt-hours'
    else:
        print int(data[-1,0])
        print data[-1,1], 'watt-hours'
