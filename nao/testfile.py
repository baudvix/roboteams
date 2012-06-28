__author__ = 'Lorenz'

import time
import math
import config
import motion_poseInit
from naoqi import ALProxy
from naoqi import ALBroker

class NAOCalibration():

    # initial definitions for Marker, IP, PORT, NXT's
    def __init__(self):
        self.IP = "194.95.174.189"
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


        # allDetectedMarker = [ Marker1, Marker2, Marker3, Marker4, Marker5, Marker6]
        # MarkerX = [alphaArray, betaArray, heightArray, idArray, [distancesToMarker] (-> calculated at last)]
        # distancesToMarker = [c, a, b] with c as the direct distance, a as the y-distance, b as the x-distance
        self.allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]

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

    def getArrayOfMarker(self):
        return self.memoryProxy.getData("LandmarkDetected")

    def resetAllDetectedMarker(self):
        self.allDetectedMarker = [[[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []], [[],[],[],[], []]]

    def detectMarkerAndCalcDist(self):
        self.resetAllDetectedMarker()

        # repeat the hole measurement numberOfMeasurements times
        for i in range(0, self.numberOfMeasurements):
            time.sleep(0.1)

            # this is the array of information about the markers (time, ids, wights, angles or nothing at all!)
            arrayOfMarker = self.getArrayOfMarker()

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

        # calculate the distances for all possible 6 markers
        for i in range(0,6):

            # only calculate if there is one marker
            if(self.allDetectedMarker[i][0] != []):

                print self.allDetectedMarker[i][0]
                self.allDetectedMarker[i][0] = self.calculateAVG(self.allDetectedMarker[i][0]) #avgAlphaArray
                self.allDetectedMarker[i][1] = self.calculateAVG(self.allDetectedMarker[i][1]) #avgBetaArray
                self.allDetectedMarker[i][2] = self.calculateAVG(self.allDetectedMarker[i][2]) #avgHeightArray
                self.allDetectedMarker[i][3] = self.mostFrequent(self.allDetectedMarker[i][3]) #avgIDArray

                distancesToMarker = [self.calculateDirectDistance(self.allDetectedMarker[i]), self.calculateXDistance(self.allDetectedMarker[i]), self.calculateYDistance(self.allDetectedMarker[i])]
                self.allDetectedMarker[i][4] = distancesToMarker

        # TODO: do not return all detected marker but only the marker with belongs to the nxt with color c
        return self.allDetectedMarker

    # this method makes the NAO look for a certain nxt (has certain color and marker numbers)
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
                for i in range(0, 5):

                    # sleep time is necessary otherwise the NAO has no chance to realize marker because of head movement
                    time.sleep(0.8)
                    arrayOfMarker = self.getArrayOfMarker()
                    #print arrayOfMarker

                    # same like in detectMarkerAndCalcDist
                    if(len(arrayOfMarker)>=2):
                        numberOfMarker = len(arrayOfMarker[1])
                    else:
                        numberOfMarker = 0

                    # Check whether we found some markers
                    if(numberOfMarker >= 1):

                        # fill array with all possible makers
                        for j in range(0, numberOfMarker):
                            try:
                                # First Field = Data field
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
                        print self.allDetectedMarker

                # calculate the averages for all detected markers and the color of the marker
                for i in range(0,6):

                    # only calculate if there is one marker
                    if(self.allDetectedMarker[i][0] != []):
                        # average ID is too error-prone!
                        #avgID = self.mostFrequent(self.allDetectedMarker[i][3])

                        avgAlpha = self.calculateAVG(self.allDetectedMarker[i][0]) #avgAlphaArray
                        avgBeta = self.calculateAVG(self.allDetectedMarker[i][1]) #avgBetaArray
                        avgSize = self.calculateAVG(self.allDetectedMarker[i][2]) #avgHeightArray

                        # TODO: make color recognition of this marker
                        if(self.markerHasColor(NXTColor, i)):
                            #motion_poseInit.setMotion(self.toDEG(getHead()[0]+avgAlpha), self.toDEG(getHead()[1]+avgBeta))
                            pass

                        # center the head of the nao to the nxt marker if the right Marker was found
                        for ID in self.allDetectedMarker[i][3]:
                            if(ID in self.markerPosition[0]):
                                motion_poseInit.setMotion(self.toDEG(self.getHead()[0]+avgAlpha), self.toDEG(self.getHead()[1]+avgBeta))
                                self.textToSpeechProxy.say('NXT with color ' + str(NXTColor) + ' found!')
                                return True

        self.textToSpeechProxy.say('NXT ' + str(NXTColor) + ' not found!')
        return False

    def markerHasColor(self, NXTColor, markerInAllDetectedMarker):
        avgSize = self.allDetectedMarker[markerInAllDetectedMarker][2]
        return True
        #return colorDetection.

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
            self.textToSpeechProxy.say('Start to calculate distance')
            allMarker = self.detectMarkerAndCalcDist()
            print allMarker
            directDistance = int(allMarker[0][4][0])
            x = int(allMarker[0][4][1])
            y = int(allMarker[0][4][2])
            orientation = self.markerPosition[1][self.markerPosition[0].index(allMarker[0][3])]

            if(len(allMarker)>0):
                self.textToSpeechProxy.say('The nxt is '+ str(directDistance) + 'centimeter away from me!')
                self.textToSpeechProxy.say('The position of the NXT is ' + str(orientation))
                return x, y, orientation
            else:
                self.textToSpeechProxy.say('Error! Could not calculate distance. Make sure that the nxt didn\'t move')
        else:
            raise NXTNotFoundException("NXT not found.")

        self.myBroker.shutdown()


n = NAOCalibration()
n.performCalibration(1)


class NXTNotFoundException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
