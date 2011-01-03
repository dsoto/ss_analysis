verbose = 0
import os
import numpy as np
import dateutil.parser
import matplotlib.dates
import datetime
numColumns = 20


def getFormattedData(circuit, beginDatetime, endDatetime, downsample, dataDirectory):
    list = [('Time Stamp',       'S14'),
            ('Watts',            'float'),
            ('Volts',            'float'),
            ('Amps',             'float'),
            ('Watt Hours SC20',  'float'),
            ('Watt Hours Today', 'float'),
            ('Max Watts',        'float'),
            ('Max Volts',        'float'),
            ('Max Amps',         'float'),
            ('Min Watts',        'float'),
            ('Min Volts',        'float'),
            ('Min Amps',         'float'),
            ('Power Factor',     'float'),
            ('Power Cycle',      'float'),
            ('Frequency',        'float'),
            ('Volt Amps',        'float'),
            ('Relay Not Closed', 'float'),
            ('Send Rate',        'float'),
            ('Machine ID',       'float'),
            ('Type',             'S8'),
            ('Credit',           'float')]    
    typeCircuit = np.dtype(list)
    typeMains = np.dtype(list[0:-1])

    if '200' in circuit:
        type = typeMains
    else:
        type = typeCircuit
    
    currentDatetime = beginDatetime
    data = []
    while currentDatetime != endDatetime:
        # construct path for certain hour of data
        path  = str(currentDatetime.year) + '/' 
        path += str(currentDatetime.month) + '/'
        path += str(currentDatetime.day) + '/'
        path += str(currentDatetime.hour) 
        path = '%02d/%02d/%02d/%02d/' % (currentDatetime.year,
                                         currentDatetime.month,
                                         currentDatetime.day,
                                         currentDatetime.hour)
        filename = '192_168_1_' + circuit + '.log'
        file = dataDirectory + path + filename

        if verbose == 1:
            print 'reading ' + file

        # read log file            
        if os.path.isfile(file):
            newData = np.loadtxt(file, delimiter=',', dtype = type, skiprows = 1)
            # if newData is only one line it is a pita so discard it
            # fixme: figure out how to append these one line logs
            if newData.shape != ():
                if data == []:
                    data = newData
                else:
                    data = np.append(data, newData, axis=0)
        
        # increment by one hour
        currentDatetime = currentDatetime + datetime.timedelta(hours=1)
        
    return data
    
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
                    numColumns = len(usecols)
                else:                        
                    usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                            11, 12, 13, 14, 15, 16, 17, 18, 20]
                    numColumns = len(usecols)
                tempData = np.loadtxt(dirname + '/' + filename, 
                                      usecols = usecols,
                                      delimiter = ',', 
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
        # decimate data by skipping 'downsample' samples
        index = range(0, data.shape[0], downsample)
        data = data[index]
    if verbose == 1:
        print data
    return data

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

def resampleData(data, column, dateStart, dateEnd, dt):
    # parsedDates are datetime objects
    print 'parsing dates'
    parsedDates = [dateutil.parser.parse(t) for t in data['Time Stamp']]
    # mplDates are days 
    mplDates = matplotlib.dates.date2num(parsedDates)
    
    
    oldSeconds = [(date - dateStart).days * 86400 + 
                  (date - dateStart).seconds for date in parsedDates]
        
    # loop through newSeconds and find new values
    # for power, if no neighboring value, power = 0
    # make newSeconds deal with dateStart and dateEnd
    totalSeconds = (dateEnd - dateStart).days * 86400 + (dateEnd - dateStart).seconds
    newSeconds = np.arange(0, totalSeconds+1, dt)

    newPower = np.zeros(len(newSeconds))
    threshold = dt
    
    if column == 'Watts':
        findMethod = 0
        if findMethod == 0: 
            print 'finding samples brute force'
            for i, second in enumerate(newSeconds):
                # find nearest oldSeconds sample
                delta = min(abs(oldSeconds - second))
                index = np.argmin(abs(oldSeconds - second))
                if delta < 15:
                    newPower[i] = data[column][index]
                    
        if findMethod == 1:
            # this section does not work yet
            print 'finding samples indexing'
            ind = 0
            for i, sec in enumerate(newSeconds):
                while 1:
                    dt1 = abs(oldSeconds[ind]-sec)
                    dt2 = abs(oldSeconds[ind+1]-sec)
                    if dt2 > dt1:
                        if dt1 < threshold:
                            newPower[i] = data[column][ind]
                        break
                    ind += 1
    if column == 'Watt Hours Today':
        ind = 0
        for i, sec in enumerate(newSeconds):
            while 1:
                if ind == len(oldSeconds) -1:
                    newPower[i] = newPower[i-1]
                    break
                dt1 = abs(oldSeconds[ind]-sec)
                dt2 = abs(oldSeconds[ind+1]-sec)
                if dt2 > dt1:
                    if dt1 < threshold:
                        newPower[i] = data[column][ind]
                    else:
                        if i == 0:
                            newPower[i] = 0
                        else:
                            newPower[i] = newPower[i-1]
                    break
                ind += 1
            
    print 'returning result'
    return newSeconds, newPower
