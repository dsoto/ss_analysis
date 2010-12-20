# calculate daily watt hours directly from watt logs
# this allows comparison between value reported by SC20

import os    
import numpy as np

# debug flag
verbose = 0
wattColumn = 1
'''
create dictionary of circuits with zero watt hours accumulated
walk directory 
load data file
convert timestamp to seconds
use to integrate watt-seconds
convert to watt-hours
add to watt-hour accumulator in dictionary
output results
'''
import dateutil.parser
import matplotlib.dates
import scipy.integrate

def integrateWatts(data):
    # could move all this into interpreter for loadtxt
    time = map(int, data[:,0])
    time = map(str, time)
    parsedDates = [dateutil.parser.parse(t) for t in time] 
    # date2num returns dates as fractions of days
    timeSeconds = matplotlib.dates.date2num(parsedDates)
    integral = scipy.integrate.trapz(data[:,1],timeSeconds)
    # convert from watt-days to watt-hours
    integral *= 24
    return integral
    
    

def printDate(date):
    outputFileList = []
    outputFileDict = {}
    wattHourDict = {}

    # generate list of log files and find last hour of logging
    for dirname, dirnames, filenames in os.walk(date):
        if verbose == 1:
            print
            print 'directory', dirname
            print 'suddirs  ', dirnames
            print 'files    ', filenames
        if filenames == []:
            if verbose == 1:
                print 'no files in this directory'
        else:
            for filename in filenames:
                if filename not in outputFileList:
                    outputFileList.append(filename)
                    wattHourDict[filename] = 0

                # open file and integrate
                integral = 0
                # construct path to file
                fullfilename = dirname + '/' + filename
                data = np.loadtxt(fullfilename, 
                                  delimiter = ',', 
                                  usecols   = (0, wattColumn), 
                                  skiprows  = 1)
                if data.shape == (2,):
                    if verbose == 1:
                        print 'one line file ignored'
                else:
                    integral = integrateWatts(data)

                wattHourDict[filename] += integral
                if verbose == 1:
                    print 'file', fullfilename
                    print 'integral', integral

    print date
    keys = wattHourDict.keys()
    keys.sort()
    for key in keys:
        print key, wattHourDict[key]
    print

# main loop
dateList = ['12/17','12/18']

for date in dateList:
    printDate(date)