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
                    wattHourDict[filename[10:13]] = 0

                # open file and integrate
                integral = 0
                # construct path to file
                fullfilename = dirname + '/' + filename
                
                if int(date[3:5]) < 16 and '200' not in filename:
                    wattColumn = 2
                else:
                    wattColumn = 1
                
                data = np.loadtxt(fullfilename, 
                                  delimiter = ',', 
                                  usecols   = (0, wattColumn), 
                                  skiprows  = 1)
                if data.shape == (2,):
                    if verbose == 1:
                        print 'one line file ignored'
                else:
                    integral = integrateWatts(data)

                wattHourDict[filename[10:13]] += integral
                if verbose == 1:
                    print 'file', fullfilename
                    print 'integral', integral

    print
    print date,
    keys = wattHourDict.keys()
    keys.sort()
    keys = ['200','201','202','203','204','205','206',
            '207','208','209','210','211','212']    
    for key in keys:
        print key, 
    print
    print '',
    for key in keys:
        if key in wattHourDict.keys():
            print "%.1f" % wattHourDict[key],
        else:
            print '0.0',
    print

# main loop
dateList = ['12/08','12/09','12/10','12/11',
            '12/12','12/13','12/14','12/15',
            '12/16','12/17','12/18','12/19']
dateList = ['12/23','12/24','12/25','12/26']

for date in dateList:
    printDate(date)