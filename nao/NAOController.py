__author__ = 'Lorenz'

import NAOCalibration
from optparse import OptionParser

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

NAO_IP = "localhost"

class queue():
    def __init__(self):
        self.arr = []

    def enqueue(self, element):
        self.arr.append(element)

    def dequeue(self):
        if(len(self.arr)>0):
            element = self.arr[0]
            self.arr = self.arr[1:len(self.arr)]
            return element
        return -1

    def first(self):
        if(len(self.arr)>0):
            return self.arr[0]
        return -1

    def last(self):
        if(len(self.arr)>0):
            return self.arr[len(self.arr)-1]
        return -1

    def len(self):
        return len(self.arr)


class NAOControllerModule(ALModule):

    def startTestCalibration(self):

        q = queue()
        # enqueue some NXTNumbers
        q.enqueue([0,"blue"])
        q.enqueue([2,"green"])
        q.enqueue([1,"red"])

        # TODO: set the normal siffness of the nao in feets so that the motor doesnt heat

        for i in range(0, q.len()):
            element = q.dequeue()
            NAOCalibration.performCalibration(element[0], element[1])


def main():
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
        "0.0.0.0",   # listen to anyone
        0,           # find a free port and use it
        pip,         # parent broker IP
        9559)       # parent broker port

    global NAOController
    NAOController = NAOControllerModule("NAOController")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
