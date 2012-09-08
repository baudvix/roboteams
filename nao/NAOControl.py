from naoqi import ALBroker
from naoqi import ALProxy
from naoqi import ALModule

from nao.NaoWalk import *
from nao.NAOCalibration import *

import time

NAO_IP="germanopen3.local"


Control = None

class NAOControlModule(ALModule):
    """ conrols behaviour of nao """

    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

    def calibrate(self, color):
        try:
            calibration = NAOCalibration()
            calibration.changeBodyOrientation("init")
            calibration.performCalibration(color)
        except NXTNotFoundException, e:
            raise e
        

    def walk(self):
        try:
            w = NaoWalk()
            w.motion.walkInit()
            w.retrieveBall()
            w.walkUpToBall()
            #send message to naoclient, that the nxt has to move, wait until nxt moved
            self.walkToPosition()
            self.__setTopCamera()
        except RedBallLostException, e:
            # w.retrieveBall()
            pass



def main():

    pip=NAO_IP
    pport=9559

    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       9560,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port

    global Control
    Control = NAOControlModule("Control")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Stopped"
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()