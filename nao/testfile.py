__author__ = 'Lorenz'

import config
from config import IP
from config import PORT
import time
import motion_poseInit
import math
from naoqi import ALProxy


nxtIDs = [64,68,80,84,85,107]
#nxts = [[nxtIDs, 'blue'], [nxtIDs, 'red'], [nxtIDs, 'yellow'], [nxtIDs, 'green']]
nxts = [[[64,68], 'blue'], [[80,84], 'red'], [[85,107], 'yellow'], [[112,108], 'green']]


yawIntervals = [0, 15, 30, 45, 60, 75, 90, -15, -30, -45, -60, -75, -90]
yawIntervalNr = 0 #0..len(yawIntervals) is possible
pitchIntervals = [0, 10, 20]
pitchIntervalNr = 0 #0..len(pitchIntervals) is possible

def look():
    for pitch in range(0, len(pitchIntervals)+1):
        print pitch
        print "yaw"
        for yaw in range(0, len(yawIntervals)+1):
            print yaw
            time.sleep(1)
            motion_poseInit.setMotion(yawIntervals[yawIntervalNr], pitchIntervals[pitchIntervalNr])
            print getHead()
            yawIntervalNr+=yawIntervalNr
        pitchIntervalNr+=pitchIntervalNr
        yawIntervalNr = 0

__author__ = 'Lorenz'

import time
import math
from naoqi import ALProxy
import config
from config import IP
from config import PORT
import motion_poseInit

#Definitions for Marker, IP, PORT, NXT's ..
#set IP and PORt of the NAO in the config file

naoCameraHeight = 50
markerHeight = 6.5
angelDeviation = 8*math.pi/180   #abweichung 8 grad

nxtIDs = [64,68,80,84,85,107]
#nxts = [[nxtIDs, 'blue'], [nxtIDs, 'red'], [nxtIDs, 'yellow'], [nxtIDs, 'green']]
nxts = [[[64,68], 'blue'], [[80,84], 'red'], [[85,107], 'yellow'], [[112,108], 'green']]

#anders loesen!
viewClear = False

##############################################################
# Create a proxy to ALLandMarkDetection
try:
    landMarkProxy = ALProxy("ALLandMarkDetection", IP, PORT)
except Exception, e:
    print "Error when creating landmark detection proxy:"
    print str(e)
    exit(1)
period = 1500
landMarkProxy.subscribe("Test_LandMark", period, 0.0 )


memValue = "LandmarkDetected"
# Create a proxy to ALMemory
try:
    memoryProxy = ALProxy("ALMemory", IP, PORT)
except Exception, e:
    print "Error when creating memory proxy:"
    print str(e)
    exit(1)
##############################################################

#runs!
def detectMarkerAndCalcDist(IP, PORT, numberOfRepitions):
    #allDetectedMarker = [ Marker1, Marker2, Marker3, Marker4, Marker5, Marker6]
    allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
    #MarkerX = [alphaArray, betaArray, heightArray, idArray, [distancesToMarker] (-> calculated at last)]
    #distancesToMarker = [c, a, b] with c as the direct distance, a as the y-distance, b as the x-distance

    #numberOfRepitions = 1

    for i in range(0, numberOfRepitions):
        time.sleep(0.1)
        val = memoryProxy.getData(memValue)

        print val
        print "--------------------------------------------------------"

        if(len(val)>=2):
            numberOfMarker = len(val[1])
        else:
            numberOfMarker = 0

        # Check whether we got a valid output.
        if(numberOfMarker >= 1):
        #if(val and isinstance(val, list) >=2 and numberOfMarker >= 1):
            # first Field = TimeStamp.
            timeStamp = val[0]

            # There can be up to 6 markers
            for j in range(0, numberOfMarker):
                try:
                    # First Field = Data field
                    markerDataField = val[1][j][0]
                    allDetectedMarker[j][0].append(markerDataField[1])    #insert the alphaValue
                    allDetectedMarker[j][1].append(markerDataField[2])    #insert the betaValue
                    allDetectedMarker[j][2].append(markerDataField[3])    #insert the sizeXValue (=sizeYValue) for the heigt

                    # Second Field = Extra info (ie, mark ID)
                    markerID = val[1][j][1][0]
                    allDetectedMarker[j][3].append(markerID) #insert the markerID

                except Exception, e:
                    print "Naomarks detected, but it seems getData is invalid. ALValue = "
                    print val
                    print "Error msg %s" % (str(e))
        else:
            print "No landmark detected"

    #calculate the distances for all 6 markers
    for i in range(0,6):
        #only calculate if there is one marker
        if(allDetectedMarker[i][0] != []):
            print allDetectedMarker[i][0]
            allDetectedMarker[i][0] = calculateAVG(allDetectedMarker[i][0]) #avgAlphaArray
            allDetectedMarker[i][1] = calculateAVG(allDetectedMarker[i][1]) #avgBetaArray
            allDetectedMarker[i][2] = calculateAVG(allDetectedMarker[i][2]) #avgHeightArray
            allDetectedMarker[i][3] = mostFrequent(allDetectedMarker[i][3]) #avgIDArray

            distancesToMarker = [calculateDirectDistance(allDetectedMarker[i]), calculateXDistance(allDetectedMarker[i]), calculateYDistance(allDetectedMarker[i])]
            allDetectedMarker[i][4] = distancesToMarker

    return allDetectedMarker

##NOT READY - DO NOT USE
def findNXT(nxtNUMBER):
    motion_poseInit.setMotion(0, 0)
    numberOfIntervalsPitch = 3
    numberOfIntervalsYaw = 13  #FIX IT!

    for g in range(0, numberOfIntervalsPitch):
        #measure for each interval
        for h in range(0, numberOfIntervalsYaw):
            allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
            #make 5 measurements before we are sure that there is (no) marker detected
            for i in range(0, 5):
                time.sleep(0.1)
                #val = memoryProxy.getData(memValue)
                val = []

                if(len(val)>=2):
                    numberOfMarker = len(val[1])
                else:
                    numberOfMarker = 0

                if(numberOfMarker >= 1):
                    #check the markerID for the right nxt
                    for j in range(0, numberOfMarker):
                        try:
                            # First Field = Data field
                            markerDataField = val[1][j][0]
                            allDetectedMarker[j][0].append(markerDataField[1])    #insert the alphaValue
                            allDetectedMarker[j][1].append(markerDataField[2])    #insert the betaValue

                            # Second Field = Extra info (ie, mark ID)
                            markerID = val[1][j][1][0]
                            allDetectedMarker[j][3].append(markerID) #insert the markerID

                        except Exception, e:
                            print "Naomarks detected, but it seems getData is invalid. ALValue = "
                            print val
                            print "Error msg %s" % (str(e))

            #if there is min one detected marker..
            if(allDetectedMarker[0][0] != []):
                #calculate the averages for all detected markers
                for i in range(0,6):
                    #only calculate if there is one marker
                    if(allDetectedMarker[i][0] != []):

                        avgID = mostFrequent(allDetectedMarker[i][3]) #avgID
                        #center the head of the nao to the nxt marker if the right Marker was found
                        if(avgID in nxts[nxtNUMBER][i]):
                            avgAlpha = calculateAVG(allDetectedMarker[i][0]) #avgAlphaArray
                            avgBeta = calculateAVG(allDetectedMarker[i][1]) #avgBetaArray
                            motion_poseInit.setMotion(toDEG(getHead()[0]+avgAlpha), toDEG(getHead()[1]+avgBeta))

            #if nothing right was found
            if(g == 0):
                moveHead(0)
            elif(g == 1):
                moveHead(10)
            elif(g == 2):
                moveHead(20)

def centerHead(alpha, beta):
    motion_poseInit.setMotion(toDEG(alpha), toDEG(beta))

#to get the current head position of the nao
def getHead():
    memoryProxy = config.loadProxy("ALMemory")
    HeadYawAngle = memoryProxy.getData("Device/SubDeviceList/HeadYaw/Position/Actuator/Value")
    HeadPitchAngle = memoryProxy.getData("Device/SubDeviceList/HeadPitch/Position/Actuator/Value")
    return HeadYawAngle, HeadPitchAngle

#this is for moving the head in intervals
def moveHead(pitch):

    alphaDEG = toDEG(getHead()[0])
    #betaDEG  = toDEG(getHead()[1])
    betaDEG = pitch

    if(alphaDEG < 4 and alphaDEG > -4):
        motion_poseInit.setMotion(15, betaDEG)

    #left
    elif(alphaDEG > 0):
        if(alphaDEG <= 75):
            motion_poseInit.setMotion(alphaDEG+15, betaDEG)
            return False
        else:
            motion_poseInit.setMotion(-15, betaDEG)
            return False

    #right
    elif(alphaDEG < 0):
        if(alphaDEG >= -75):
            motion_poseInit.setMotion(alphaDEG-15, betaDEG)
            return False
        else:
            motion_poseInit.setMotion(0, betaDEG)
            return False

def calculateAVG(array):
    avg = 0
    if(array != []):
        for elem in array:
            avg+=elem
        return avg/len(array)

def mostFrequent(lst):
    return max(set(lst), key=lst.count)

def calculateDirectDistance(marker): #xy
    beta = marker[1]
    betaHeadPos = getHead()[1]
    return abs((naoCameraHeight-markerHeight)/math.tan(beta + angelDeviation + betaHeadPos))

def calculateYDistance(marker): #y
    alpha = marker[0]
    alphaHeadPos = getHead()[0]
    return abs(math.sin(math.pi/2-alpha+alphaHeadPos)*calculateDirectDistance(marker))

def calculateXDistance(marker): #x
    alpha = marker[0]
    alphaHeadPos = getHead()[0]
    return abs(math.cos(math.pi/2-alpha+alphaHeadPos)*calculateDirectDistance(marker))

def toRAD(number):
    return number*math.pi/180

def toDEG(number):
    return number*180/math.pi

def main():
    #allMarker = detectMarkerAndCalcDist(IP, PORT, 10)
    findNXT(0)
    print allMarker

main()