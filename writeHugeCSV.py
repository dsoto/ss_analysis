import datetime
import os
import dateutil.parser


def constructPath(currentDatetime):
    '''
    given a datetime object, this function creates a path name that 
    matches the sheeva file directory structure for data logs
    '''
    path = '%02d/%02d/%02d/%02d/' % (currentDatetime.year,
                                     currentDatetime.month,
                                     currentDatetime.day,
                                     currentDatetime.hour)
    path = dataDirectory + path
    return path

def constructCircuitList():
    '''
    returns a list of filenames from 192_168_1_200.log
    through 192_168_1_212.log
    '''
    circuitList = range(200,213)
    circuitList = map(str, circuitList)
    fileCircuitList = []
    for circuit in circuitList:
        fileCircuitList.append('192_168_1_' + circuit + '.log')
    return fileCircuitList

def openFiles(path, fileCircuitList):
    '''
    attempts to open every circuit's log file in 'path' and returns
    a dictionary with keys that are the filenames and values that
    are the open file objects
    '''
    fileDict = {}
    for circuit in fileCircuitList:
        file = path + circuit
        if os.path.isfile(file):
            fileDict[circuit] = open(file, 'r')
    return fileDict
    
def getNewFiles(timeStamp, fileCircuitList):
    '''
    helper function to open new log files 
    '''
    path = constructPath(timeStamp)       
    fileDict = openFiles(path, fileCircuitList)
    return fileDict

def initializeLineDict():
    lineDict = {}
    # discard header line
    for key in fileDict.keys():
        line = fileDict[key].readline()
        lineDict[key] = line
    # keep first data line
    for key in fileDict.keys():
        line = fileDict[key].readline()
        lineDict[key] = line
    # print out dict
    return lineDict

def initializeTimeStampDict(lineDict):
    timeStampDict = {}
    for key in lineDict.keys():
        timeStampDict[key] = getTimeStampFromLine(lineDict[key])
    return timeStampDict

def getTimeStampFromLine(line):
    lineTimeStamp = dateutil.parser.parse(line[0:14])
    return lineTimeStamp

def getNextUniqueTimeStampFromFile(key, timeStamp, file):
    while 1:
        # read next line in file
        lineDict[key] = fileDict[key].readline()
        # read next time stamp
        newTimeStamp = getTimeStampFromLine(lineDict[key])
        if newTimeStamp > timeStamp:
            timeStampDict[key] = newTimeStamp
            break
        # if we encounter last file, remove dict entry
    return

def writeCircuitData(circuit):
    data = lineDict[circuit]
    data = data.strip()
    data = data.split(',')
    if circuit == '192_168_1_200.log':
        columnList = [1,2,3,4,5]
    else:
        columnList = [1,2,3,4,5,20]
    for col in columnList:
        csv.write(data[col]+',')

def writeCircuitNoData(circuit):
    if circuit == '192_168_1_200.log':
        csv.write(',' * 5)
    else:
        csv.write(',' * 6)

def printHeader():
    csv.write('date,')
    circuit = '200'
    for col in ['watts','volts','amps','watt hours SC20','watt hours today']:
        csv.write(circuit+'_'+col+',')
    circuitList = range(201,213)
    circuitList = map(str, circuitList)
    for circuit in circuitList:
        for col in ['watts','volts','amps','watt hours SC20','watt hours today','credit']:
            csv.write(circuit+'_'+col+',')


dateRangeStart = datetime.datetime(2011, 1, 01, 0)
dateRangeEnd   = datetime.datetime(2011, 2, 01, 0)
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'
fileCircuitList = constructCircuitList()

csv = open('big.csv','w')
printHeader()
            
timeStamp = dateRangeStart
fileDict = getNewFiles(timeStamp, fileCircuitList)
lineDict = initializeLineDict()
timeStampDict = initializeTimeStampDict(lineDict)
    

# iterate by second from dateRangeStart to dateRange end
while timeStamp != dateRangeEnd:
    # if sample exists in any file, write out timestamp
    if timeStamp in timeStampDict.values():
        csv.write('\n')
        csv.write(str(timeStamp)+',')
        # loop through all circuits looking for data at this timestamp
        for circuit in fileCircuitList:
            # does circuit have open file?
            if circuit in timeStampDict.keys():
                # if circuit has open file and
                # timestamp matches, write out circuit information
                if timeStamp == timeStampDict[circuit]:
                    writeCircuitData(circuit)
                    getNextUniqueTimeStampFromFile(circuit, timeStamp, file)
                # if circuit has open file and 
                # if timestamp does not match, write out empty circuit
                else:
                    writeCircuitNoData(circuit)
            # if circuit has no open file, write out empty circuit
            else:
                writeCircuitNoData(circuit)

    # increment timestamp and deal with hour change if necessary
    oldtimeStamp = timeStamp
    timeStamp = timeStamp + datetime.timedelta(seconds=1)
    if oldtimeStamp.hour != timeStamp.hour:
        print timeStamp
        fileDict = getNewFiles(timeStamp, fileCircuitList)
        lineDict = initializeLineDict()
        timeStampDict = initializeTimeStampDict(lineDict)

csv.close()