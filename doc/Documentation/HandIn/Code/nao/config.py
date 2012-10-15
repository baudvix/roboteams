import motion
import math
from naoqi import ALProxy

IP = "localhost"
NAO_PORT = 9559
NAO_IP = '194.95.174.188'

def loadProxy(pName):
    proxy = ALProxy(pName, IP, PORT)
    return proxy

def standUp():
    #TODO:
    pass

def StiffnessOn(proxy, partOfBody):
    #We use the "Body" name to signify the collection of all joints
    pNames = partOfBody #"Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def StiffnessOff(proxy, partOfBody):
    #We use the "Body" name to signify the collection of all joints
    pNames = partOfBody #"Body"
    pStiffnessLists = 0.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def setStiffness(proxy, partOfBody, pStiffnessLists):
    #We use the "Body" name to signify the collection of all joints
    pNames = partOfBody #"Body"
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def setHeadMotion(motionProxy, headYawAngle, headPitchAngle):
    motionProxy.angleInterpolation("HeadPitch", math.pi*headPitchAngle/180,1,True)
    motionProxy.angleInterpolation("HeadYaw", math.pi*headYawAngle/180,1,True)

def naoWalkTo(x, y, theta):
    print "naoWalkTo"
    motionProxy = loadProxy("ALMotion")
    #motionProxy.walkInit()
    walkPoseInit(motionProxy)
    motionProxy.walkTo(x, y, theta)

def calibrationPoseInit(motionProxy, pMaxSpeedFraction = 0.2):
    StiffnessOn(motionProxy, "Body")

    # Define The Initial Position
    HeadYawAngle       = 0
    HeadPitchAngle     = 0

    ShoulderPitchAngle = 80
    ShoulderRollAngle  = 20
    ElbowYawAngle      = -80
    ElbowRollAngle     = -60
    WristYawAngle      = 0
    HandAngle          = 0

    HipYawPitchAngle   = 0
    HipRollAngle       = 0
    HipPitchAngle      = -54 #changed from -20
    KneePitchAngle     = 120 #changed from 40
    AnklePitchAngle    = -68 #changed from -20
    AnkleRollAngle     = 0

    # Get the Robot Configuration
    robotConfig = motionProxy.getRobotConfig()
    robotName = ""
    for i in range(len(robotConfig[0])):
        if (robotConfig[0][i] == "Model Type"):
            robotName = robotConfig[1][i]

    if (robotName == "naoH25") or\
       (robotName == "naoAcademics"):


        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, +ElbowYawAngle, +ElbowRollAngle, WristYawAngle, HandAngle]
        RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, -ElbowYawAngle, -ElbowRollAngle, WristYawAngle, HandAngle]

        LeftLeg  = [HipYawPitchAngle, +HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, +AnkleRollAngle]
        RightLeg = [HipYawPitchAngle, -HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, -AnkleRollAngle]

    elif (robotName == "naoH21") or\
         (robotName == "naoRobocup"):

        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, +ElbowYawAngle, +ElbowRollAngle]
        RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, -ElbowYawAngle, -ElbowRollAngle]

        LeftLeg  = [HipYawPitchAngle, +HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, +AnkleRollAngle]
        RightLeg = [HipYawPitchAngle, -HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, -AnkleRollAngle]

    elif (robotName == "naoT14"):

        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, +ElbowYawAngle, +ElbowRollAngle, WristYawAngle, HandAngle]
        RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, -ElbowYawAngle, -ElbowRollAngle, WristYawAngle, HandAngle]

        LeftLeg  = []
        RightLeg = []

    elif (robotName == "naoT2"):

        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = []
        RightArm = []

        LeftLeg  = []
        RightLeg = []

    # Gather the joints together
    pTargetAngles = Head + LeftArm + LeftLeg + RightLeg + RightArm

    # Convert to radians
    pTargetAngles = [x * motion.TO_RAD for x in pTargetAngles]

    #------------------------------ send the commands -----------------------------
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    # Ask motion to do this with a blocking call
    motionProxy.angleInterpolationWithSpeed(pNames, pTargetAngles, pMaxSpeedFraction)

    motionProxy.stiffnessInterpolation("Body", 0.1, 1.0)
    StiffnessOn(motionProxy, "Head")

def walkPoseInit(motionProxy, pMaxSpeedFraction = 0.2):
    StiffnessOn(motionProxy, "Body")

    # Define The Initial Position
    HeadYawAngle       = 0
    HeadPitchAngle     = 0

    ShoulderPitchAngle = 80
    ShoulderRollAngle  = 20
    ElbowYawAngle      = -80
    ElbowRollAngle     = -60
    WristYawAngle      = 0
    HandAngle          = 0

    HipYawPitchAngle   = 0
    HipRollAngle       = 0
    HipPitchAngle      = -20
    KneePitchAngle     = 40
    AnklePitchAngle    = -20
    AnkleRollAngle     = 0

    # Get the Robot Configuration
    robotConfig = motionProxy.getRobotConfig()
    robotName = ""
    for i in range(len(robotConfig[0])):
        if (robotConfig[0][i] == "Model Type"):
            robotName = robotConfig[1][i]

    if (robotName == "naoH25") or\
       (robotName == "naoAcademics"):


        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, +ElbowYawAngle, +ElbowRollAngle, WristYawAngle, HandAngle]
        RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, -ElbowYawAngle, -ElbowRollAngle, WristYawAngle, HandAngle]

        LeftLeg  = [HipYawPitchAngle, +HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, +AnkleRollAngle]
        RightLeg = [HipYawPitchAngle, -HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, -AnkleRollAngle]

    elif (robotName == "naoH21") or\
         (robotName == "naoRobocup"):

        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, +ElbowYawAngle, +ElbowRollAngle]
        RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, -ElbowYawAngle, -ElbowRollAngle]

        LeftLeg  = [HipYawPitchAngle, +HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, +AnkleRollAngle]
        RightLeg = [HipYawPitchAngle, -HipRollAngle, HipPitchAngle, KneePitchAngle, AnklePitchAngle, -AnkleRollAngle]

    elif (robotName == "naoT14"):

        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, +ElbowYawAngle, +ElbowRollAngle, WristYawAngle, HandAngle]
        RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, -ElbowYawAngle, -ElbowRollAngle, WristYawAngle, HandAngle]

        LeftLeg  = []
        RightLeg = []

    elif (robotName == "naoT2"):

        Head     = [HeadYawAngle, HeadPitchAngle]

        LeftArm  = []
        RightArm = []

        LeftLeg  = []
        RightLeg = []

    # Gather the joints together
    pTargetAngles = Head + LeftArm + LeftLeg + RightLeg + RightArm

    # Convert to radians
    pTargetAngles = [x * motion.TO_RAD for x in pTargetAngles]

    #------------------------------ send the commands -----------------------------
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    # Ask motion to do this with a blocking call
    motionProxy.angleInterpolationWithSpeed(pNames, pTargetAngles, pMaxSpeedFraction)

    motionProxy.stiffnessInterpolation("Body", 1.0, 0.1)
    StiffnessOn(motionProxy, "Head")

def poseZero(proxy):
    # We use the "Body" name to signify the collection of all joints and actuators
    pNames = "Body"

    # Get the Number of Joints
    numBodies = len(proxy.getJointNames(pNames))

    # We prepare a collection of floats
    pTargetAngles = [0.0] * numBodies

    # We set the fraction of max speed
    pMaxSpeedFraction = 0.3

    # Ask motion to do this with a blocking call
    proxy.angleInterpolationWithSpeed(pNames, pTargetAngles, pMaxSpeedFraction)
