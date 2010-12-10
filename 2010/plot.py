'''
'''

import os
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.dates
verbose = 0

def getData(plotCircuit, plotDate, downsample):
    if verbose == 1:
        print 'getting data for', plotCircuit, plotDate
    data = []
    for dirname, dirnames, filenames in os.walk(plotDate):
        for filename in filenames:
            if plotCircuit in filename:
                if verbose ==1:
                    print 'getting data for', dirname
                tempData = np.loadtxt(dirname+'/'+filename, 
                                      delimiter=',', 
                                      usecols = range(19),
                                      skiprows = 1)
                # deal with case of one line file
                if data == []:
                    data = tempData
                elif tempData.shape == (19,):
                    tempData.reshape(1,19)
                else:
                    data = np.append(data, tempData, axis=0)
    # check for nonexistent data
    if data != []:
        index = range(0, data.shape[0], downsample)
        data = data[index]
                    
    return data

# create dictionary of header strings
def getHeaderStrings():
    headerString = 'Time Stamp,Credit,Watts,Volts,Amps,Watt Hours SC20,Watt Hours Today,Max Watts,Max Volts,Max Amps,Min Watts,Min Volts,Min Amps,Power Factor,Power Cycle,Frequency,Volt Amps,Relay Not Closed,Send Rate,Machine ID,Type'
    headers = headerString.split(',')
    d = {}
    for i,h in enumerate(headers):
        d[i]=h
    return d

plotColumn = 2
plotDate = '12/07'
plotCircuitList = ['201','202','203','204','205','206','207','208','209','210','211','212']
#plotCircuitList = ['201','202','203','205','206','207','209','210','211','212']
downsample = 20
d = getHeaderStrings()

fig = plt.figure()
axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))


# create circuits loop here
for plotCircuit in plotCircuitList:
    # walk through files and generate temp file-like object
    data = getData(plotCircuit, plotDate, downsample)
    
    if data != []:
        # map time from float to int and then to string
        time = map(int, data[:,0])
        time = map(str, time)
        
        parsedDates = [dateutil.parser.parse(t) for t in time]
        
        # date2num returns a float number of seconds to represent date
        mplDates = matplotlib.dates.date2num(parsedDates)
        
        axis.plot_date(mplDates, data[:,plotColumn], '.', label=plotCircuit)


# figure out how to set range from midnight to midnight
print d[plotColumn]
print plotDate
print plotCircuitList

dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
axis.xaxis.set_major_formatter(dateFormatter)
axis.set_xlabel("time of day")
axis.set_ylabel(d[plotColumn])
axis.legend(loc=(1.0,0.0))
plotFileName = plotDate[0:2] + plotDate[3:5] + '_' + d[plotColumn]
print plotFileName
fig.savefig(plotFileName + ".pdf")
#plt.show()














'''
import os

# create empty list of open filenames
outputFileList = []
outputFileDict = {}

# open date
# open file
# if name is not in list, add to list, create file
# append file to existing file, discarding header line

for dirname, dirnames, filenames in os.walk('12/'):
    if filenames == []:
        print 'no files in this directory'
    else:
        print dirname, dirnames, filenames
        for filename in filenames:
            if filename not in outputFileList:
                # append name to list
                outputFileList.append(filename)
                # create output file of same name in outputDirectory
                outputFileName = 'concatenated/' + filename
                # create entry in dictionary with filename and file object
                outputFileDict[filename] = open(outputFileName,'w')
            
            # open existing data file
            inputFileName = dirname + '/' + filename
            inputFile = open(inputFileName, 'r')
            
            # discard first line (should be header)
            inputFile.readline()
            
            # copy to concatenated file
            data = inputFile.read()
            inputFile.close()
            outputFileDict[filename].write(data)
                
# tidy up by closing all files
for filename in outputFileList:
    print filename
    outputFileDict[filename].close()        
    



# create dictionary of header strings
headerString = 'Time Stamp,Credit,Watts,Volts,Amps,Watt Hours SC20,Watt Hours Today,Max Watts,Max Volts,Max Amps,Min Watts,Min Volts,Min Amps,Power Factor,Power Cycle,Frequency,Volt Amps,Relay Not Closed,Send Rate,Machine ID,Type'
headers = headerString.split(',')
d = {}
for i,h in enumerate(headers):
    d[i]=h
    

import numpy as np
import matplotlib.pyplot as plt

# glob data files
import glob
fileNameList = glob.glob('*.log')

import dateutil.parser
import matplotlib.dates

fig = plt.figure()
axis = fig.add_axes((0.1, 0.1, 0.7, 0.8))

# loop through, plot and label with filename
for fileName in fileNameList:

    # open data file
    data = np.loadtxt(fileName, delimiter=',', usecols = range(19))
    
    # map time from float to int and then to string
    time = map(int, data[:,0])
    time = map(str, time)
    
    parsedDates = [dateutil.parser.parse(t) for t in time]
    
    # date2num returns a float number of seconds to represent date
    mplDates = matplotlib.dates.date2num(parsedDates)
    
    column = 6
    if '200' in fileName:
        # offset because mains file has no credit column
        power = data[:,column - 1]
    else:
        power = data[:,column]

    axis.plot_date(mplDates, power, '.', label=fileName[10:13])

dateFormatter = matplotlib.dates.DateFormatter('%H:%M')
axis.xaxis.set_major_formatter(dateFormatter)
axis.set_xlabel("time of day")
axis.set_ylabel(d[column])
axis.legend(loc=(1.0,0.0))
fig.savefig(d[column] + ".pdf")
plt.show()

'''