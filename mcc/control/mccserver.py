from twisted.protocols import amp
from twisted.internet import reactor, task, defer
from twisted.internet.protocol import _InstanceFactory, Factory

from mcc.control import command
#from mcc.model import roboter

import random

class MCCProtocol(amp.AMP):

    def register(self, type, color=None):
        print 'Got a new roboter: type=%d color=%d' % (type, color)
        return {'handle': 0}
    command.Register.responder(register)

    def activate(self, handle):
        print '#%d Roboter activated' % handle
        return {'ACK': 'got activate'}
    command.Activate.responder(activate)

    def nxt_calibrated(self, handle, nxt_handle, x, y, yaw):
        print '#%d NXT calibrated #%d (%d, %d, %d)' % (handle, nxt_handle, x, y, yaw)
        return {'ACK': 'got calibrated'}
    command.NXTCalibrated.responder(nxt_calibrated)

    def nxt_spotted(self, handle, nxt_handle):
        print '#%d Roboter spotted NXT #%d' % ( handle, nxt_handle)
        return {'ACK': 'got spotted'}
    command.NXTSpotted.responder(nxt_spotted)

    def send_data(self,handle, point_tag, x, y, yaw):
        print '#%d Send data %d: (%d, %d, %d)' % (handle, point_tag, x, y, yaw)
        return{'ACK': 'got data'}
    command.SendData.responder(send_data)

    def arrived_point(self, handle, x, y):
        print '#%d Arrived at (%d. %d)' % (handle, x, y)
        return {'ACK': 'got arrival'}
    command.ArrivedPoint.responder(arrived_point)

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print 'Connection Lost to Client ', reason

class MCCFactory(Factory):

    protocol = MCCProtocol

    def __init__(self, reactor, instance, deferred):
        self.tmp = 'TODO'
        self.clients = []


class MCCServer(object):

    def __init__(self):
        self.protocol = None
        self.host = 'localhost'
        self.port = 5000
        self.robots = None
        self.listen()
        loop = task.LoopingCall(self.run)
        loop.start(0.5)
        print 'MCC is started and listens on %d' % self.port
        reactor.run()

    def listen(self):
        deffered = defer.Deferred()
        if self.protocol is not None:
            self.protocol.transport.loseConnection()
        factory = MCCFactory(reactor, MCCProtocol, deffered)
        connector = reactor.listenTCP(self.port, factory)
        deffered.addCallback(self.listening)
        deffered.addErrback(self.failure)
        return deffered

    def listening(self):
        print 'listening'

    def failure(self, error):
        print 'Error: %s:%s\n%s' % (self.host, self.port, error)

    def run(self):
        """

        """

def main():
    server = MCCServer()

if __name__ == '__main__':
    main()