__author__ = 'Lorenz'

<<<<<<< HEAD
import sys
sys.path.append("/home/guenthse/uni/semesterprojekt/naoqi")
print sys.path
=======
import NAOCalibration
from optparse import OptionParser

class queue():
    def __init__(self):
        self.arr = []

    def enqueue(self, element):
        self.arr.append(element)
>>>>>>> nao-master

import NAOCalibration
from twisted.internet.protocol import Protocol
from twisted.internet import reactor, task, defer
from twisted.internet.protocol import Factory
from mcc.utils import Point
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

class NAOProtocol(Protocol):
    
    def __init__(self, factory):
        self.factory = factory
        
    def started(self):
        pass
        
    def connectionMade(self):
        speechProxy = ALProxy("ALTextToSpeech")
        speechProxy.say("Connection to MCC established")
        
    def nxtCalibration(self, color=None):
        pass
        
    def trackRedball(self):
        pass

    def initialPosition(self):
        pass

#    def standUp(self):
        
#    def sitDown(self):
        
    def moveToPoint(self, Point):
        pass
        
    def getPath(self,  path):
        pass
        
    def connectionLost(self, reason):
        pass

class NAOFactory(Factory):
    def buildProtocol(self, addr):
        return NAOProtocol()
        
class NAOServer():
    
    def __init__(self):
        self.host = localhost
        self.port = 5000
        self.endpoint = TCP4ServerEndpoint(reactor, 5000)
        self.endpoint.listen(NAOFactory)
        reactor.run()
        
def main():
    #initiate: set stiffness, stand up
    
    #wait for MCC to start / broadcast "I'm ready" until response from MCC
    
    #
    server = NAOServer()

if __name__ == '__main__':
    main()
