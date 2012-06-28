__author__ = 'rob'
import time
import math
import motion
from naoqi import ALBroker
from naoqi import ALProxy

class NaoWalk():

    def __init__(self):
        self.myBroker = ALBroker("myBroker","0.0.0.0",0,"germanopen3.local",9559)
        self.motion = ALProxy("ALMotion")
        self.tracker = ALProxy("ALRedBallTracker")
        self.tracker.setWholeBodyOn(False)
        self.tracker.startTracker()
        self.ballPosition = []
        self.targetPosition = []
        self.isLost = True

    def __del__(self):
        #self.tracker.stopTracker()
        pass

    def __checkForBall(self):
        argument = self.tracker.isNewData()
        if argument == True:
            self.tracker.getPosition()
            return argument
        if argument == False:
            self.tracker.getPosition()
            return argument

    def retrieveBall(self):
        self.motion.walkInit()
        for turnAngle in [0,math.pi/2,math.pi/2,math.pi/2]:
            if turnAngle > 0:
                self.motion.walkTo(0,0,turnAngle)
            if self.hasBall():
                self.turnToBall()
                return
            for headPitchAngle in [((math.pi*29)/180),((math.pi*12)/180)]:
                self.motion.angleInterpolation("HeadPitch", headPitchAngle,0.3,True)
                for headYawAngle in [-((math.pi*40)/180),-((math.pi*20)/180),0,((math.pi*20)/180),((math.pi*40)/180)]:
                    self.motion.angleInterpolation("HeadYaw",headYawAngle,0.3,True)
                    time.sleep(0.3)
                    if self.hasBall():
                        self.turnToBall()
                        return


        
    def turnToBall(self):
        if self.hasBall():
            self.ballPosition = self.tracker.getPosition()
        b = self.ballPosition[1]/self.ballPosition[0]
        dist = math.sqrt(math.pow(self.ballPosition[0],2) + math.pow(self.ballPosition[1],2))
        print str(dist)
        z = math.atan(b)
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.motion.walkTo(0,0,z)

    def hasBall(self):
        self.__checkForBall()
        time.sleep(0.5)
        if self.__checkForBall():
            return True
        else :
            return False


    def turnToBallPerHeadAngle(self):
        headangle = self.motion.getAngles("HeadYaw",False)
        self.motion.post.walkTo(0,0,headangle[0])

    def test(self):
        self.ballPosition = self.tracker.getPosition()
        print str(self.ballPosition[0])
        print str(self.ballPosition[1])

    def safePosition(self):
        self.hasBall()
        if self.hasBall():
            self.targetPosition = self.tracker.getPosition()
        else :
            return false

    def walkToPosition(self):
        x = self.targetPosition[0]/2 + 0.05
        y = self.targetPosition[1]/2
        dist = math.sqrt(math.pow(self.ballPosition[0],2) + math.pow(self.ballPosition[1],2))
        if dist > 1.3:
            y -= 0.05
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.motion.walkTo(x,y,0)


