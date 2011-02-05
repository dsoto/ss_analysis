import datetime
import os

dataDirectory = '/Users/dsoto/Dropbox/metering_-_Berkley-CU/Mali/Shake down/SD Card logs/logs/'

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
    print timeStamp
    path = constructPath(timeStamp)       
    fileDict = openFiles(path, fileCircuitList)
    print fileDict
    return fileDict

dateRangeStart = datetime.datetime(2011, 1, 01)
dateRangeEnd = datetime.datetime(2011, 1, 02)

timeStamp = dateRangeStart

fileCircuitList = constructCircuitList()
fileDict = getNewFiles(timeStamp, fileCircuitList)

# iterate by second from dateRangeStart to dateRange end
while timeStamp != dateRangeEnd:
    oldtimeStamp = timeStamp
    timeStamp = timeStamp + datetime.timedelta(seconds=1)
    if oldtimeStamp.hour != timeStamp.hour:
        fileDict = getNewFiles(timeStamp, fileCircuitList)

        
# open all files in fileList structure

# when hour changes
# make file path based on datetime hour
#

# open first line of each file
# peel off date and convert to datetime object

# compare timeCounter to each dateCircuit
# if no matches: increment timeCounter
# for each match, write out 
