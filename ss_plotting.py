verbose = 0
import os
import numpy as np
import dateutil.parser
import matplotlib.dates
import datetime
numColumns = 20


def getFormattedData(circuit, beginDatetime, endDatetime, downsample, dataDirectory):
    # get formats together for arrays
    namesCircuit = ['Time Stamp',
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
                'Type',
                'Credit']    
    namesMains = namesCircuit[0:-1]
    formatsCircuit = ['S14',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'float',
                  'S8',
                  'float']
    formatsMains = formatsCircuit[0:-1]    
    typeCircuit = np.dtype({'names':namesCircuit, 'formats':formatsCircuit})
    typeMains = np.dtype({'names':namesMains, 'formats':formatsMains})

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
            #print newData
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
