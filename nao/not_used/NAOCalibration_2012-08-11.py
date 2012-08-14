__author__ = 'Lorenz'

import sys
import time
import math
import config
import motion_poseInit
import colourDetection
from naoqi import ALProxy
from naoqi import ALBroker

class NAOCalibration():

    # initial definitions for Marker, IP, PORT, NXT's
    def __init__(self):
        self.IP = "localhost"
        self.PORT = 9559
        self.naoCameraHeight = 41 # 50cm if NAO stands, 41 if NAO is in "knee position"
        self.markerHeight = 18
        self.angelDeviation = 8 * math.pi/180   #abweichung 8 grad
        self.numberOfMeasurements = 5

        # ['back', 'front', 'front left', 'front right', 'back left', 'back right']
        self.markerPosition = [[119, 84, 64, 80, 68, 114], [0, 180, 120, 240, 60, 300]]
        self.colors = ['red', 'green', 'blue', 'black']

        # this are the current intervals in degree in which the NAO looks for the nxt
        self.pitchIntervals = [25, 5]
        self.yawIntervals = [0, -35, 35]

        self.resolutionHeight = 400
        self.resolutionWidth = 680

        # allDetectedMarker = [ Marker1, Marker2, Marker3, Marker4, Marker5, Marker6]
        # MarkerX = [alphaArray, betaArray, heightArray, idArray, [distancesToMarker] (-> calculated at last)]
        # distancesToMarker = [c, a, b] with c as the direct distance, a as the y-distance, b as the x-distance
        self.allDetectedMarker = [] #[[[],[],[],[],[]], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
        self.allDetectedMarkerAVG = [] #[[[],[],[],[],[]], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
        self.allDetectedMarkerLastMeasurement = []
        self.allDetectedMarkerAVGLastMeasurement = []

        # listen to anyone # find a free port and use it # parent broker IP # parent broker port
        self.myBroker = ALBroker("myBroker", "0.0.0.0", 0, self.IP, self.PORT)
        self.landMarkProxy = self.startLandmarkProxy()
        self.memoryProxy = self.startMemoryProxy()
        self.motionProxy = self.startMotionProxy()
        self.textToSpeechProxy = self.startALProxy()

    def startLandmarkProxy(self):
        # Create a proxy to ALLandMarkDetection
        try:
            landMarkProxy = ALProxy("ALLandMarkDetection", self.IP, self.PORT)
        except Exception, e:
            print "Error when creating landmark detection proxy:"
            print str(e)
            exit(1)
        period = 1500
        landMarkProxy.subscribe("Test_LandMark", period, 0.0 )
        return landMarkProxy

    def startMemoryProxy(self):
        # Create a proxy to ALMemory
        try:
            memoryProxy = ALProxy("ALMemory", self.IP, self.PORT)
        except Exception, e:
            print "Error when creating memory proxy:"
            print str(e)
            exit(1)
        return memoryProxy

    def startMotionProxy(self):
        # Create a proxy to Motion
        try:
            motionProxy = config.loadProxy("ALMotion")
        except Exception, e:
            print "Error when creating motion proxy:"
            print str(e)
            exit(1)
        return motionProxy

    def startALProxy(self):
        # Create a proxy to ALMemory
        try:
            tts = ALProxy("ALTextToSpeech")
        except Exception, e:
            print "Error when creating ALProxy:"
            print str(e)
            exit(1)
        return tts

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
                # the first field contains the time - not in use yet
                timeStamp = arrayOfMarker[0]

                #if(numberOfMarker > 6):
                #    print "numberOfMarker = ", numberOfMarker

                # There can be up to X markers (more than 6 marker possible!)
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
                print str(i) + " No landmark detected!"

    def resetAllDetectedMarker(self):
        # this is a safe copy for the case if the NAO finds the marker from nxt with the right color but can not find the marker again in measureAgainAndCalcDist
        self.allDetectedMarkerLastMeasurement = self.allDetectedMarker
        self.allDetectedMarkerAVGLastMeasurement = self.allDetectedMarkerAVG

        self.allDetectedMarker = [] #[[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
        self.allDetectedMarkerAVG = [] #[[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]

    def calcAvgOfAllDetectedMarker(self):
        # calculate the distances for all possible markers
        if(self.allDetectedMarker != []):
            for i in range(0,len(self.allDetectedMarker)):

                # only calculate if there is one marker
                if(self.allDetectedMarker[i][0] != []):

                    self.allDetectedMarkerAVG[i][0] = self.calculateAVG(self.allDetectedMarker[i][0]) #avgAlphaArray
                    self.allDetectedMarkerAVG[i][1] = self.calculateAVG(self.allDetectedMarker[i][1]) #avgBetaArray
                    self.allDetectedMarkerAVG[i][2] = self.calculateAVG(self.allDetectedMarker[i][2]) #avgHeightArray
                    self.allDetectedMarkerAVG[i][3] = self.mostFrequent(self.allDetectedMarker[i][3]) #avgIDArray

        # also calculate the distances for the measurements before
        if(self.allDetectedMarkerLastMeasurement != []):

            for i in range(0,len(self.allDetectedMarkerLastMeasurement)):
                # only calculate if there is one marker
                if(self.allDetectedMarkerLastMeasurement[i][0] != []):

                    self.allDetectedMarkerAVGLastMeasurement[i][0] = self.calculateAVG(self.allDetectedMarkerLastMeasurement[i][0]) #avgAlphaArray
                    self.allDetectedMarkerAVGLastMeasurement[i][1] = self.calculateAVG(self.allDetectedMarkerLastMeasurement[i][1]) #avgBetaArray
                    self.allDetectedMarkerAVGLastMeasurement[i][2] = self.calculateAVG(self.allDetectedMarkerLastMeasurement[i][2]) #avgHeightArray
                    self.allDetectedMarkerAVGLastMeasurement[i][3] = self.mostFrequent(self.allDetectedMarkerLastMeasurement[i][3]) #avgIDArray


    def measureAgainAndCalcDist(self):
        self.detectMarker(3) # again for better results

        # if any marker could find again (this is the normal procedure)
        if(self.allDetectedMarker != []):
            # update the average values
            self.calcAvgOfAllDetectedMarker()

            for i in range(0,len(self.allDetectedMarker)):

                # only calculate if there is one marker
                if(self.allDetectedMarker[i][0] != []):

                    distancesToMarker = [self.calculateDirectDistance(self.allDetectedMarkerAVG[i]), self.calculateXDistance(self.allDetectedMarkerAVG[i]), self.calculateYDistance(self.allDetectedMarkerAVG[i])]
                    self.allDetectedMarker[i][4] = distancesToMarker
                    self.allDetectedMarkerAVG[i][4] = distancesToMarker

        # in this case the marker could not find again after (seldom but possible)
        else:
            print "MarkerNotFoundError: Could not find marker again! - using old measurments to calculate distance"

            if(self.allDetectedMarkerLastMeasurement != []):
                # update the average values
                self.calcAvgOfAllDetectedMarker()

            for i in range(0,len(self.allDetectedMarker)):

                # only calculate if there is one marker
                if(self.allDetectedMarker[i][0] != []):

                    distancesToMarker = [self.calculateDirectDistance(self.allDetectedMarkerAVG[i]), self.calculateXDistance(self.allDetectedMarkerAVG[i]), self.calculateYDistance(self.allDetectedMarkerAVG[i])]
                    self.allDetectedMarker[i][4] = distancesToMarker
                    self.allDetectedMarkerAVG[i][4] = distancesToMarker
            return False

        return True


    def getNearestMarker(self, allDetectedMarkerAVGLastOrCurrentMeasurement, allDetectedMarkerLastOrCurrentMeasurement):
        dist = -1
        minDist = -1
        nearest = -1
        for i in range(0, len(allDetectedMarkerAVGLastOrCurrentMeasurement)):
            if(allDetectedMarkerAVGLastOrCurrentMeasurement != []):
                if(allDetectedMarkerAVGLastOrCurrentMeasurement[i][0] != []):
                    dist = math.sqrt(abs(allDetectedMarkerAVGLastOrCurrentMeasurement[i][0]) + abs(allDetectedMarkerAVGLastOrCurrentMeasurement[i][1]))

                    if(dist < minDist or minDist == -1):
                        minDist = dist
                        nearest = i
        if(nearest != -1):
            return allDetectedMarkerAVGLastOrCurrentMeasurement[nearest], allDetectedMarkerLastOrCurrentMeasurement[nearest]
        return []


    def findNXT(self, NXTColor):

        # set the initial head position for NAO
        config.setHeadMotion(self.motionProxy, 0, 0)

        # move head vertical
        for g in range(0, len(self.pitchIntervals)):

            # move head horizontal
            for h in range(0, len(self.yawIntervals)):

                # set the head position to the current yaw and pitch interval
                config.setHeadMotion(self.motionProxy, self.yawIntervals[h], self.pitchIntervals[g])

                #make 5 measurements to be sure that there is / is no marker detected
                self.detectMarker(5)

                # calculate the averages for all detected markers
                self.calcAvgOfAllDetectedMarker()

                found = self.centerHeadToMarkerToDetectColor(NXTColor)
                if(found != -1):
                    print 'NXT with color' + str(self.colors[NXTColor]) + ' found!'
                    self.textToSpeechProxy.say('NXT with color' + str(self.colors[NXTColor]) + ' found!')
                    return True

        print 'NXT ' + str(NXTColor) + ' not found!'
        self.textToSpeechProxy.say('NXT ' + str(NXTColor) + ' not found!')
        return False

    # called by findNXT
    # centers the head to the marker with the color NXTColor which was found first
    def centerHeadToMarkerToDetectColor(self, NXTColor):
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

    def getXPixelWithYawAngle(self, yawAngle):
        return yawAngle

    #to get the current head position of the nao
    def getHead(self):
        memoryProxy = config.loadProxy("ALMemory")
        HeadYawAngle = memoryProxy.getData("Device/SubDeviceList/HeadYaw/Position/Actuator/Value")
        HeadPitchAngle = memoryProxy.getData("Device/SubDeviceList/HeadPitch/Position/Actuator/Value")
        return HeadYawAngle, HeadPitchAngle

    def calculateAVG(self, array):
        avg = 0
        if(array != []):
            for elem in array:
                avg+=elem
            return avg/len(array)

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

    def performCalibration(self, color):

        print "#01 Try to find NXT with color: ", str(self.colors[color])
        found = self.findNXT(color)

        if(found):
            # now the head of the nao should be centred to the right colored marker
            # then calc again to get better data
            print "#02 Colored NXT found! Measure again to get accurate Distance."
            markerFoundAgain = self.measureAgainAndCalcDist()

            if(markerFoundAgain):
                print "#03a Calc distance"
                self.textToSpeechProxy.say('Calculate distance')
                cM_ = self.getNearestMarker(self.allDetectedMarkerAVG, self.allDetectedMarker)
                centerMarkerAVG = cM_[0]
                centerMarker = cM_[1]
                print "Center Marker: ", str(centerMarker)

            # we have to use here the older measurements to calculate
            else:
                print "#03b Calc distance"
                self.textToSpeechProxy.say('Calculate distance')
                cM_ = self.getNearestMarker(self.allDetectedMarkerAVGLastMeasurement, self.allDetectedMarkerLastMeasurement)
                centerMarkerAVG = cM_[0]
                centerMarker = cM_[1]
                print "Center Marker: ", str(centerMarker)

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

class NXTNotFoundException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def main():
    n = NAOCalibration()
    config.walkPoseInit(n.motionProxy)
    config.calibrationPoseInit(n.motionProxy)

    n.performCalibration(0) #search for red nxt
    #print "------------------------------------------"
    #n.performCalibration(1) #search for green nxt
    #print "------------------------------------------"
    #n.performCalibration(2) #search for blue nxt

    #config.walkPoseInit(n.motionProxy)
    sys.exit(1)

if __name__ == '__main__':
    main()