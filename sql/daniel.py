from sql.analysis import *

import datetime as dt


def calculateEuclidianDistance(powerVector1, powerVector2):
    return sum((powerVector2 - powerVector1)**2)**(0.5)



cid = 25

if __name__ == "__main__":
    vector1 = getAveragedPowerForCircuit(cid,
                                         dt.datetime(2011, 06, 20),
                                         dt.datetime(2011, 06, 27))
    print vector1

    vector2 = getAveragedPowerForCircuit(cid,
                                         dt.datetime(2011, 06, 26),
                                         dt.datetime(2011, 06, 27))
    print vector2

    print calculateEuclidianDistance(vector1, vector2)