__author__ = 'Lorenz'

import time
import math
from naoqi import ALProxy
import config
from config import IP
from config import PORT
import motion_poseInit
from naoqi import ALBroker
from naoqi import ALModule

# listen to anyone # find a free port and use it # parent broker IP # parent broker port
myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)

#Definitions for Marker, IP, PORT, NXT's ..
#set IP and PORt of the NAO in the config file
naoCameraHeight = 50
markerHeight = 12
angelDeviation = 8*math.pi/180   #abweichung 8 grad

nxtIDs = [64,68,80,84,85,107]
#nxts = [[nxtIDs, 'blue'], [nxtIDs, 'red'], [nxtIDs, 'yellow'], [nxtIDs, 'green']]
#nxts = [[[64,68,84,80,114,119], 'blue'], [[80,84], 'red'], [[85,107], 'yellow'], [[112,108], 'green']]
nxts = [[[119, 84, 64, 80, 68, 114], ['back', 'front', 'front left', 'front right', 'back left', 'back right'], 'blue'], [[80,84], 'red'], [[85,107], 'yellow'], [[112,108], 'green']]
#nxt0 = [[119, 84, 64, 80, 68, 114], ['back', 'front', 'front left', 'front right', 'back left', 'back right']]

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


def detectMarkerAndCalcDist(IP, PORT, numberOfRepitions):
    #allDetectedMarker = [ Marker1, Marker2, Marker3, Marker4, Marker5, Marker6]
    allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
    #MarkerX = [alphaArray, betaArray, heightArray, idArray, [distancesToMarker] (-> calculated at last)]
    #distancesToMarker = [c, a, b] with c as the direct distance, a as the y-distance, b as the x-distance

    #numberOfRepitions = 1
    for i in range(0, numberOfRepitions):
        time.sleep(0.1)
        val = memoryProxy.getData(memValue)

        #print val
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
    pitchIntervals = [10, 20, 0]
    yawIntervals = [0, -30, 30, -60, 60]
    numberOfIntervalsPitch = len(pitchIntervals)
    numberOfIntervalsYaw = len(yawIntervals)

    for g in range(0, numberOfIntervalsPitch):
        #measure for each interval
        print 'g' +str(g)
        for h in range(0, numberOfIntervalsYaw):
            print 'h' +str(h)
            motion_poseInit.setMotion(yawIntervals[h], pitchIntervals[g])
            allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
            #make 5 measurements before we are sure that there is (no) marker detected
            for i in range(0, 5):
                time.sleep(0.5)
                val = memoryProxy.getData(memValue)

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
                            #transmitt HeadPosition to verify the color for nxt
                            tts = ALProxy("ALTextToSpeech")
                            tts.say('Marker' + str(avgID) + 'from NXT ' + str(nxtNUMBER) + ' found')
                            tts.say('The position of the NXT is ' + nxts[nxtNUMBER][1][nxts[0][0].index(avgID)])
                            return True

    tts = ALProxy("ALTextToSpeech")
    tts.say('NXT not found!')
    return False

#to get the current head position of the nao
def getHead():
    memoryProxy = config.loadProxy("ALMemory")
    HeadYawAngle = memoryProxy.getData("Device/SubDeviceList/HeadYaw/Position/Actuator/Value")
    HeadPitchAngle = memoryProxy.getData("Device/SubDeviceList/HeadPitch/Position/Actuator/Value")
    return HeadYawAngle, HeadPitchAngle

#not needed any more!!
def moveHead():
    alphaDEG = toDEG(getHead()[0])
    betaDEG  = toDEG(getHead()[1])

    if(alphaDEG < 4 and alphaDEG > -4):
        motion_poseInit.setMotion(30, betaDEG)

    #left
    elif(alphaDEG > 0):
        if(alphaDEG <= 90):
            motion_poseInit.setMotion(alphaDEG+30, betaDEG)
            return False
        else:
            motion_poseInit.setMotion(-30, betaDEG)
            return False

    #right
    elif(alphaDEG < 0):
        if(alphaDEG >= -90):
            motion_poseInit.setMotion(alphaDEG-30, betaDEG)
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
    pitchHeadPos = getHead()[1]
    return abs((naoCameraHeight-markerHeight)/math.tan(beta + angelDeviation + pitchHeadPos))

def calculateYDistance(marker): #y
    alpha = marker[0]
    yawHeadPos = getHead()[0]
    print "y"
    print math.sin(math.pi/2-alpha+yawHeadPos)
    print math.pi/2-alpha+yawHeadPos
    return abs(math.sin(math.pi/2-alpha+yawHeadPos)*calculateDirectDistance(marker))

def calculateXDistance(marker): #x
    alpha = marker[0]
    yawHeadPos = getHead()[0]
    print "x"
    print math.cos(math.pi/2-alpha+yawHeadPos)
    print math.pi/2-alpha+yawHeadPos
    return abs(math.cos(math.pi/2-alpha+yawHeadPos)*calculateDirectDistance(marker))

def toRAD(number):
    return number*math.pi/180

def toDEG(number):
    return number*180/math.pi

def main():
    proxy = config.loadProxy("ALMotion")
    config.StiffnessOn(proxy)
    config.PoseInit(proxy)

    found = findNXT(0)
    tts = ALProxy("ALTextToSpeech")
    if(found):
        tts.say('Start to calculate distance')
        allMarker = detectMarkerAndCalcDist(IP, PORT, 10)
        print allMarker
        if(len(allMarker)>0):
            tts.say('The nxt is '+ str(int(allMarker[0][4][0])) + 'centemeter away from me!')

    myBroker.shutdown()

main()