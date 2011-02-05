import datetime
import os
import dateutil.parser

def constructPath(currentDatetime):
    '''
    given a datetime object, this function creates a path name that 
    matches the sheeva file directory structure for data logs
    '''
    path  = str(currentDatetime.year) + '/' 
    path += str(currentDatetime.month) + '/'
    path += str(currentDatetime.day) + '/'
    path += str(currentDatetime.hour) 
    path = '%02d/%02d/%02d/%02d/' % (currentDatetime.year,
                                     currentDatetime.month,
                                     currentDatetime.day,
                                     currentDatetime.hour)
    path = dataDirectory + path
    return path

def constructCircuitList():
    '''
    returns a list of filenames from 192_168_1_200
    through 192_168_1_212
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


dateRangeStart = datetime.datetime(2011, 1, 01, 0)
dateRangeEnd   = datetime.datetime(2011, 1, 01, 1)
dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'
fileCircuitList = constructCircuitList()

csv = open('big.csv','w')

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
        for circuit in fileCircuitList:
            if circuit in timeStampDict.keys():
                if timeStamp == timeStampDict[circuit]:
                    csv.write(circuit+',')
                    getNextUniqueTimeStampFromFile(circuit, timeStamp, file)
                else:
                    csv.write(circuit[10:13] + ',')
            else:
               csv.write(circuit[10:13] + ',')
    # increment timestamp and deal with hour change if necessary
    oldtimeStamp = timeStamp
    timeStamp = timeStamp + datetime.timedelta(seconds=1)
    if oldtimeStamp.hour != timeStamp.hour:
        fileDict = getNewFiles(timeStamp, fileCircuitList)


csv.close()       
# open all files in fileList structure

# when hour changes
# make file path based on datetime hour
#

# open first line of each file
# peel off date and convert to datetime object

# compare timeCounter to each dateCircuit
# if no matches: increment timeCounter
# for each match, write out 
