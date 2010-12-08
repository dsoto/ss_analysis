# script to scrape log files for daily use

import os    
import numpy as np

# debug flag
verbose = 0

def printDate(date):
    outputFileList = []
    outputFileDict = {}
    wattHourDict = {}

    # generate list of log files and find last hour of logging
    for dirname, dirnames, filenames in os.walk(date):
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
        if verbose == 1:
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
            timeStamp = int(data[0])
            totalWattHour = data[1]
        else:
            timeStamp = int(data[-1,0])
            totalWattHour = data[-1,1]
        
        if verbose == 1:
            print timeStamp, 'time of last log'
            print totalWattHour, 'watt-hours'
        
        wattHourDict[key] = totalWattHour
    
    # output lines for spreadsheet
    
    print
    print date    
    for key in keys:
        print key[-7:-4],
    print
    for key in keys:
        print wattHourDict[key],
    print
    

# main loop
dateList = ['12/02','12/03','12/04','12/05','12/06']

for date in dateList:
    printDate(date)