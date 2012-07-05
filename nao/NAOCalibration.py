__author__ = 'Lorenz'

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
        self.naoCameraHeight = 50
        self.markerHeight = 12
        self.angelDeviation = 8 * math.pi/180   #abweichung 8 grad
        self.numberOfMeasurements = 5

        # ['back', 'front', 'front left', 'front right', 'back left', 'back right']
        self.markerPosition = [[119, 84, 64, 80, 68, 114], [0, 180, 120, 240, 60, 300]]

        # this are the current intervals in degree in which the NAO looks for the nxt
        self.pitchIntervals = [0, 10, 20]
        self.yawIntervals = [0, -30, -60, 0, 30, 60]

        self.resolutionHeight = 400
        self.resolutionWidth = 680

        # allDetectedMarker = [ Marker1, Marker2, Marker3, Marker4, Marker5, Marker6]
        # MarkerX = [alphaArray, betaArray, heightArray, idArray, [distancesToMarker] (-> calculated at last)]
        # distancesToMarker = [c, a, b] with c as the direct distance, a as the y-distance, b as the x-distance
        self.allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
        self.allDetectedMarkerAVG = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]

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
            time.sleep(0.6)

            # this is the array of information about the markers (time, ids, wights, angles or nothing at all!)
            arrayOfMarker = self.memoryProxy.getData("LandmarkDetected")

            # set the number of recognized markers on nxt's
            if(len(arrayOfMarker)>=2):
                numberOfMarker = len(arrayOfMarker[1])
            else:
                numberOfMarker = 0

            # Check whether we found some markers
            if(numberOfMarker >= 1):
                # the first field contains the time - not in use yet
                timeStamp = arrayOfMarker[0]

                # There can be up to 6 markers
                for j in range(0, numberOfMarker):
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
                print "No landmark detected"

    def resetAllDetectedMarker(self):
        self.allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]
        self.allDetectedMarkerAVG = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]

    def calcAvgOfAllDetectedMarker(self):
        # calculate the distances for all possible 6 markers
        for i in range(0,len(self.allDetectedMarker)):

            # only calculate if there is one marker
            if(self.allDetectedMarker[i][0] != []):

                self.allDetectedMarkerAVG[i][0] = self.calculateAVG(self.allDetectedMarker[i][0]) #avgAlphaArray
                self.allDetectedMarkerAVG[i][1] = self.calculateAVG(self.allDetectedMarker[i][1]) #avgBetaArray
                self.allDetectedMarkerAVG[i][2] = self.calculateAVG(self.allDetectedMarker[i][2]) #avgHeightArray
                self.allDetectedMarkerAVG[i][3] = self.mostFrequent(self.allDetectedMarker[i][3]) #avgIDArray


    def measureAgainAndCalcDist(self):
        self.detectMarker(8)
        # update the average values
        self.calcAvgOfAllDetectedMarker()

        for i in range(0,len(self.allDetectedMarker)):

            # only calculate if there is one marker
            if(self.allDetectedMarker[i][0] != []):

                distancesToMarker = [self.calculateDirectDistance(self.allDetectedMarkerAVG[i]), self.calculateXDistance(self.allDetectedMarkerAVG[i]), self.calculateYDistance(self.allDetectedMarkerAVG[i])]
                self.allDetectedMarker[i][4] = distancesToMarker
                self.allDetectedMarkerAVG[i][4] = distancesToMarker


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


    def findNXT(self, NXTColor):

        # set the initial head position for NAO
        motion_poseInit.setMotion(0, 0)

        # move head vertical
        for g in range(0, len(self.pitchIntervals)):

            # move head horizontal
            for h in range(0, len(self.yawIntervals)):

                # set the head position to the current yaw and pitch interval
                motion_poseInit.setMotion(self.yawIntervals[h], self.pitchIntervals[g])

                #make 5 measurements to be sure that there is / is no marker detected
                self.detectMarker(5)

                # calculate the averages for all detected markers
                self.calcAvgOfAllDetectedMarker()

                # TODO: make more effective
                found = self.centerHeadToMarkerWithColor(NXTColor)
                if(found != -1):
                    self.textToSpeechProxy.say('NXT with color' + str(NXTColor) + ' found!')
                    return True

        self.textToSpeechProxy.say('NXT ' + str(NXTColor) + ' not found!')
        return False

    # called by findNXT
    # centers the head to the marker with the color NXTColor which was found first
    def centerHeadToMarkerWithColor(self, NXTColor):
        for i in range(0, len(self.allDetectedMarker)):

            # only calculate if there is one marker
            if(self.allDetectedMarker[i][0] != []):

                avgAlpha = self.allDetectedMarkerAVG[i][0]
                avgBeta = self.allDetectedMarkerAVG[i][1]
                motion_poseInit.setMotion(self.toDEG(self.getHead()[0]+avgAlpha), self.toDEG(self.getHead()[1]+avgBeta))

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

        config.StiffnessOn(self.motionProxy)
        config.PoseInit(self.motionProxy)

        found = self.findNXT(color)

        if(found):
            # now the head of the nao should be centred to the right colored marker
            # then calc again to get better data
            self.measureAgainAndCalcDist()

            self.textToSpeechProxy.say('Calculate distance')
            centerMarker = self.getNearestMarker()[0]
            centerMarkerAVG = self.getNearestMarker()[1]
            print "Center Marker"
            print centerMarker

            if(centerMarker!=[]):
                directDistance = int(centerMarker[4][0])
                x = int(centerMarker[4][1])
                y = int(centerMarker[4][2])
                print x
                print y
                IDs = centerMarker[3]
                for i in range(0, len(IDs)):
                    if(IDs[i] in self.markerPosition[0]):
                        orientation = self.markerPosition[1][self.markerPosition[0].index(centerMarker[3])]
                        self.textToSpeechProxy.say('The nxt is '+ str(directDistance) + 'centimeter away from me!')
                        self.textToSpeechProxy.say('The position of the NXT is ' + str(orientation))
                        return x, y, orientation
                    else:
                        raise NXTNotFoundException("Unknown ID found!")
            else:
                self.textToSpeechProxy.say('Error! Could not calculate distance. Make sure that the nxt didn\'t move')
                raise NXTNotFoundException("Could not calculate distance. Make sure that the nxt didn\'t move.")
        else:
            raise NXTNotFoundException("NXT not found.")

        self.myBroker.shutdown()

class NXTNotFoundException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


n = NAOCalibration()
colors = ['red', 'yellow', 'green', 'blue']
n.performCalibration(3)
