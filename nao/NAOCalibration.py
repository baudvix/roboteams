__author__ = 'Lorenz'

import sys
import time
import math
import config
import colourDetection
from naoqi import ALProxy
from naoqi import ALBroker

class NAOCalibration():

    # initial definitions for Marker, IP, PORT, NXT's
    def __init__(self):
        self.IP = "localhost"
        self.PORT = 9559
        #will be set when the NAO when changeBodyOrientation is called
        #if nao stands it is 50cm if nao is in knee position it is 41 cm
        self.naoCameraHeight = 0
        self.markerHeight = 18 #7 if on the ground
        self.angelDeviation = 8 * math.pi/180   #abweichung 8 grad
        self.numberOfMeasurements = 5
        self.bodyOrientation = ""

        # NEU MACHEN: !!['back', 'front', 'front left', 'front right', 'back left', 'back right']
        # 0 bzw. 360 (front), 60 (rechts vorn), 120 (rechts hinten), 180 (hinten), 240 (links hinten), 300 (links vorn)
        self.markerPosition = [[119, 84, 80, 68, 64, 114], [0, 180, 120, 240, 60, 300]]
        self.colors = ['red', 'green', 'blue', 'black']

        # this are the current intervals in degree in which the NAO looks for the nxt
        self.pitchIntervals = [25, 5]
        self.yawIntervals = [0, -35, 35]

        self.resolutionHeight = 400
        self.resolutionWidth = 680

        # allDetectedMarker = [ Marker1, Marker2, Marker3, Marker4, Marker5, Marker6]
        # MarkerX = [alphaArray, betaArray, heightArray, idArray, [distancesToMarker] (-> calculated at last)]
        # distancesToMarker = [c, a, b] with c as the direct distance, a as the y-distance, b as the x-distance
        self.allDetectedMarker = []
        self.allDetectedMarkerAVG = []

        # listen to anyone # find a free port and use it # parent broker IP # parent broker port
        self.myBroker = ALBroker("myBroker", "0.0.0.0", 0, self.IP, self.PORT)
        self.landMarkProxy = self.startLandmarkProxy()
        self.memoryProxy = self.startMemoryProxy()
        self.motionProxy = self.startMotionProxy()
        self.textToSpeechProxy = self.startTTSProxy()

    def startLandmarkProxy(self):
        # Create a proxy to ALLandMarkDetection
        try:
            landMarkProxy = ALProxy("ALLandMarkDetection", self.IP, self.PORT)
        except Exception, e:
            print "Error when creating landmark detection proxy: "
            print str(e)
            exit(1)
        period = 500 #changed from 1500! change back
        landMarkProxy.subscribe("Test_LandMark", period, 0.0 )
        return landMarkProxy

    def startMemoryProxy(self):
        # Create a proxy to ALMemory
        try:
            memoryProxy = ALProxy("ALMemory", self.IP, self.PORT)
        except Exception, e:
            print "Error when creating memory proxy: "
            print str(e)
            exit(1)
        return memoryProxy

    def startMotionProxy(self):
        # Create a proxy to Motion
        try:
            motionProxy = ALProxy("ALMotion", self.IP, self.PORT)
        except Exception, e:
            print "Error when creating motion proxy: "
            print str(e)
            exit(1)
        return motionProxy

    def startTTSProxy(self):
        # Create a proxy to ALMemory
        try:
            tts = ALProxy("ALTextToSpeech")
        except Exception, e:
            print "Error when creating TTSProxy: "
            print str(e)
            exit(1)
        return tts

    def resetAllDetectedMarker(self):
        self.allDetectedMarker = [] #[[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
        self.allDetectedMarkerAVG = [] #[[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]

    def calcAvgOfAllDetectedMarker(self):
        # calculate the distances for all possible markers
        for i in range(0,len(self.allDetectedMarker)):

            # only calculate if there is one marker
            if(self.allDetectedMarker[i][0] != []):

                self.allDetectedMarkerAVG[i][0] = self.calculateAVG(self.allDetectedMarker[i][0]) #avgAlphaArray
                self.allDetectedMarkerAVG[i][1] = self.calculateAVG(self.allDetectedMarker[i][1]) #avgBetaArray
                self.allDetectedMarkerAVG[i][2] = self.calculateAVG(self.allDetectedMarker[i][2]) #avgHeightArray
                self.allDetectedMarkerAVG[i][3] = self.mostFrequent(self.allDetectedMarker[i][3]) #avgIDArray

    def getNearestMarker(self):
        dist = -1
        minDist = -1
        nearest = -1
        for i in range(0, len(self.allDetectedMarkerAVG)):
            if(self.allDetectedMarkerAVG[i][0] != []):
                dist = math.sqrt(abs(self.allDetectedMarkerAVG[i][0]) + abs(self.allDetectedMarkerAVG[i][1]))

                if(dist < minDist or minDist == -1):
                    minDist = dist
                    nearest = i
        if(nearest != -1):
            return self.allDetectedMarkerAVG[nearest], self.allDetectedMarker[nearest]
        return []

    #calculates the average value of an array with numbers
    def calculateAVG(self, array):
        avg = 0
        if(array != []):
            for elem in array:
                avg+=elem
            return avg/len(array)

    #gives back the most frequent element in a list with any types
    def mostFrequent(self, lst):
        return max(set(lst), key=lst.count)

    def calculateDirectDistance(self, marker): #xy
        beta = marker[1]
        pitchHeadPos = self.getHead()[1]
        return abs((self.naoCameraHeight-self.markerHeight)/math.tan(beta + self.angelDeviation + pitchHeadPos))

    def calculateYDistance(self, marker): #y
        alpha = marker[0]
        yawHeadPos = self.getHead()[0]
        return abs(math.sin(math.pi/2-alpha+yawHeadPos)*self.calculateDirectDistance(marker))

    def calculateXDistance(self, marker): #x
        alpha = marker[0]
        yawHeadPos = self.getHead()[0]
        return abs(math.cos(math.pi/2-alpha+yawHeadPos)*self.calculateDirectDistance(marker))

    def toRAD(self, number):
        return number*math.pi/180

    def toDEG(self, number):
        return number*180/math.pi

        # This is a method for finding any NAOMarker with a certain Color (NXTColor) - at least this finds the NXTs


        # called by findColouredMarker

    #to get the current head position of the nao
    def getHead(self):
        HeadYawAngle = self.memoryProxy.getData("Device/SubDeviceList/HeadYaw/Position/Actuator/Value")
        HeadPitchAngle = self.memoryProxy.getData("Device/SubDeviceList/HeadPitch/Position/Actuator/Value")
        return HeadYawAngle, HeadPitchAngle

    def measureAgainAndCalcDist(self):
        self.detectMarker(3)

        if(self.allDetectedMarker != []):
            # update the average values
            self.calcAvgOfAllDetectedMarker()

            for i in range(0,len(self.allDetectedMarker)):

                # only calculate if there is one marker
                if(self.allDetectedMarker[i][0] != []):

                    distancesToMarker = [self.calculateDirectDistance(self.allDetectedMarkerAVG[i]), self.calculateXDistance(self.allDetectedMarkerAVG[i]), self.calculateYDistance(self.allDetectedMarkerAVG[i])]
                    self.allDetectedMarker[i][4] = distancesToMarker
                    self.allDetectedMarkerAVG[i][4] = distancesToMarker
        else:
            print "MarkerNotFoundError: Could not find marker again!"
            return False

        return True

    # centers the head to the marker with the color NXTColor which was found first
    def centerHeadToMarkerWithColor(self, NXTColor):
        currentHeadPosition = self.getHead()

        for i in range(0, len(self.allDetectedMarker)):
            config.setHeadMotion(self.motionProxy, self.toDEG(currentHeadPosition[0]), self.toDEG(currentHeadPosition[1]))

            # only calculate if there is one marker
            if(self.allDetectedMarker[i][0] != []):
                print str(i) + " "
                avgAlpha = self.allDetectedMarkerAVG[i][0]
                avgBeta = self.allDetectedMarkerAVG[i][1]
                print "head centred to one detected marker to get the color"
                config.setHeadMotion(self.motionProxy, self.toDEG(self.getHead()[0]+avgAlpha), self.toDEG(self.getHead()[1]+avgBeta))

                if(colourDetection.getColour(self.IP, self.PORT, 320, 240) == NXTColor):
                    # head is centered to the right marker with the color of nxt
                    return i
        return -1

    def detectMarker(self, numberOfMeasurements):
        self.resetAllDetectedMarker()

        # repeat the hole measurement numberOfMeasurements times
        for i in range(0, numberOfMeasurements):
            time.sleep(0.5)

            # this is the array of information about the markers (time, ids, wights, angles or nothing at all!)
            arrayOfMarker = self.memoryProxy.getData("LandmarkDetected")

            # set the number of recognized markers on nxt's
            if(len(arrayOfMarker)>=2):
                numberOfMarker = len(arrayOfMarker[1])
            else:
                numberOfMarker = 0

            # Check whether we found some markers
            if(numberOfMarker >= 1):
                print str(i) + "Any landmark detected."
                print arrayOfMarker
                # the first field contains the time - not in use yet
                timeStamp = arrayOfMarker[0]

                if(numberOfMarker > 6):
                    print "numberOfMarker = ", numberOfMarker

                # There can be up to X markers (more than 6 markers possible!)
                for j in range(0, numberOfMarker):
                    self.allDetectedMarker.append([[],[],[],[],[]])
                    self.allDetectedMarkerAVG.append([[],[],[],[],[]])

                    try:
                        # First Field = Data field with the angles and sizes
                        markerDataField = arrayOfMarker[1][j][0]
                        self.allDetectedMarker[j][0].append(markerDataField[1])    #insert the alphaValue
                        self.allDetectedMarker[j][1].append(markerDataField[2])    #insert the betaValue
                        self.allDetectedMarker[j][2].append(markerDataField[3])    #insert the sizeXValue (=sizeYValue) for the height

                        # Second Field = Extra info (ie, mark ID)
                        markerID = arrayOfMarker[1][j][1][0]
                        self.allDetectedMarker[j][3].append(markerID) #insert the markerID

                    except Exception, e:
                        print "Naomarks detected, but it seems getData is invalid. ALValue = "
                        print arrayOfMarker
                        print "Error msg %s" % (str(e))
            else:
                # this should not happen because before method starts nao enshures that the head centres the right marker
                print str(i) + "No landmark detected!"

    def findColouredMarker(self, NXTColor):

        # set the initial head position for NAO
        config.setHeadMotion(self.motionProxy, 0, 0)

        # move head vertical
        for g in range(0, len(self.pitchIntervals)):
            print "g: ", str(g)
            # move head horizontal
            for h in range(0, len(self.yawIntervals)):
                print "h: ", str(h)
                # set the head position to the current yaw and pitch interval
                config.setHeadMotion(self.motionProxy, self.yawIntervals[h], self.pitchIntervals[g])

                #make 5 measurements to be sure that there is / is no marker detected
                self.detectMarker(5)

                # calculate the averages for all detected markers
                self.calcAvgOfAllDetectedMarker()

                # now we prove for every found maker if it has the right color
                found = self.centerHeadToMarkerWithColor(NXTColor)
                if(found != -1):
                    print 'NXT with color ' + str(self.colors[NXTColor]) + ' found!'
                    self.textToSpeechProxy.say('NXT with color ' + str(self.colors[NXTColor]) + ' found!')
                    return True

        print 'NXT with color ' + str(self.colors[NXTColor]) + ' not found!'
        self.textToSpeechProxy.say('NXT with color ' + str(self.colors[NXTColor]) + ' not found!')
        return False

    def performCalibration(self, color):

        print "#01 Try to find NXT with color: ", str(self.colors[color])
        self.textToSpeechProxy.say("Trying to find "+ str(self.colors[color])+ " NXT")
        found = self.findColouredMarker(color)

        if(found):
            # now the head of the nao should be centred to the right colored marker
            # then calc again to get better data
            print "#02 Colored NXT found! Measure again to get accurate Distance."
            markerFoundAgain = self.measureAgainAndCalcDist()

            if(markerFoundAgain == True):
                print "#03 Calc distance"
                self.textToSpeechProxy.say('Calculate distance')
                centerMarkerAVG = self.getNearestMarker()[0]
                centerMarker = self.getNearestMarker()[1]
                print "Center Marker"
                print centerMarker

                if(centerMarker!=[]):
                    directDistance = int(centerMarker[4][0])
                    x = int(centerMarker[4][1])
                    y = int(centerMarker[4][2])
                    print "x", str(x)
                    print "y", str(y)
                    IDs = centerMarker[3]
                    for i in range(0, len(IDs)):
                        if(IDs[i] in self.markerPosition[0]):
                            orientation = self.markerPosition[1][self.markerPosition[0].index(IDs[i])]
                            print "orientation", str(orientation), "directDist", str(directDistance), "x", str(x), "y", str(y)
                            self.textToSpeechProxy.say('The nxt is '+ str(directDistance) + 'centimeter away from me!')
                            #self.textToSpeechProxy.say('The position of the NXT is ' + str(orientation))
                            return x, y, orientation
                        else:
                            print "#Error2 Marker doesn't match to NXT!"
                            return -1
                            #raise NXTNotFoundException("Unknown ID found!")
                else:
                    self.textToSpeechProxy.say('Error! Could not calculate distance. Make sure that the nxt didn\'t move')
                    print "#Error1 could not detect marker in the center of view"
                    return -1
                    #raise NXTNotFoundException("Could not calculate distance. Make sure that the nxt didn\'t move.")
        else:
            print "#Error0 NXT with right color not found!"
            return -1
            #raise NXTNotFoundException("NXT not found.")

        self.myBroker.shutdown()

    def changeBodyOrientation(self, orientation):
        if(orientation == "init"):
            self.bodyOrientation = "init"
            self.naoCameraHeight = 50
            config.walkPoseInit(self.motionProxy)
        elif(orientation == "knee"):
            self.bodyOrientation = "knee"
            self.naoCameraHeight = 41
            config.calibrationPoseInit(self.motionProxy)
        elif(orientation == "zero"):
            self.bodyOrientation = "zero"
            self.naoCameraHeight = 52
            config.poseZero(self.motionProxy)

class NXTNotFoundException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def main():
    print "-----begin:NAOCalibration-----"

    n = NAOCalibration()
    n.changeBodyOrientation("init")

    print "-------look for red NXT---------"

    n.performCalibration(0) # red
    print "-------look for green NXT---------"
    #n.performCalibration(1) # green
    print "-------look for blue NXT---------"
    #n.performCalibration(2) # blue

    config.setHeadMotion(n.motionProxy, 0, 0)

    n.changeBodyOrientation("knee")

    print "-----end:NAOCalibration-----"
    sys.exit(1)

if __name__ == '__main__':
    main()

class NXTNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)