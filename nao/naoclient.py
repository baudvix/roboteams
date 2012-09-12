import pprint
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
from mcc.control import command
from nao.NAOCalibration import *
from naoqi import ALProxy
from naoqi import ALBroker

NAOControl = None

class RobotProtocol(amp.AMP):

    def update_state(self, state):
        print 'Updating state to %d' % state
        return {'ack': 'got state'}
    command.UpdateState.responder(update_state)

    def update_position(self, x_axis, y_axis, yaw):
        print 'Updating position (%d, %d, %d)' % (x_axis, y_axis, yaw)
        return {'ack': 'got position'}
    command.UpdatePosition.responder(update_position)

    def send_map(self, map):
        print 'Updating map '
        pprint.pprint(map)
        return {'ack': 'got map'}
    command.SendMap.responder(send_map)


class NXTProtocol(RobotProtocol):
    def go_to_point(self, x_axis, y_axis):
        print 'Going to Point (%d, %d)' % (x_axis, y_axis)
        return {'ack': 'got point'}
    command.GoToPoint.responder(go_to_point)


class NAOProtocol(RobotProtocol):

    def nxt_missing(self, nxt_handle, color):
        print 'Searching for NXT #%d, color=%d' % (nxt_handle, color)
        return {'ack': 'searching'}
    command.NXTMissing.responder(nxt_missing)

    def perform_calibration(self, nao_handle, nxt_handle, color):
        print 'Performing calibration on NXT #%d, color=%d' % (nxt_handle, color)
        try:
            calibrationResult = NAOControl.calibrate(color)
            return {'handle': nao_handle,'nxt_handle': nxt_handle,'x_axis':calibrationResult[0],'y_axis':calibrationResult[1],'yaw': calibrationResult[2]}
        except NXTNotFoundException, e:
            print e
    command.PerformCalibration.responder(perform_calibration)

    def send_path(self, nxt_handle, path):
        print 'Following red ball on path'
        pprint.pprint(path)
        for way in path:
            NAOControl.followRedBall('first')
            deffered = protocol.callRemote(command.NXTFollowed, handle = protocol.self.handle, nxt_handle = nxt_handle, x_axis = path[0], y_axis = path[1])
            deffered.addCallback(NAOControl.followRedBall('second'))
            NAOControl.followRedBall('second')
        return {'ack': 'followed path'}
    command.SendPath.responder(send_path)


class RobotFactory(_InstanceFactory):
    def __init__(self, reactor, instance, deferred):
        _InstanceFactory.__init__(self, reactor, instance, deferred)


class NAOClient():

    def __init__(self):
        self.protocol = None
        self.host = '194.95.174.187'
        self.port = 5000
        self.color = 0
        self.handle = None
        self.active = False
        self.robot_type = 1
        self.connect()
        self.connectToNao()
        loop = task.LoopingCall(self.run)
        loop.start(1.0)
        reactor.run()

    def run(self):
        pass

    def connect(self):
        deferred = defer.Deferred()
        if self.protocol is not None:
            self.protocol.transport.loseConnection()
        factory = RobotFactory(reactor, NAOProtocol(), deferred)
        reactor.connectTCP(self.host, self.port, factory)
        deferred.addCallback(self.connected)
        deferred.addErrback(self.failure)
        return deferred

    def connected(self, protocol):
        self.protocol = protocol
        print 'connected to mcc'
        deffered = protocol.callRemote(command.Register, robot_type=self.robot_type, color=self.color)
        deffered.addCallback(self.activate)
        deffered.addErrback(self.failure)

    def activate(self, handle):
        self.handle = handle['handle']
        print self.handle
        deffered = self.protocol.callRemote(command.Activate, handle=self.handle)
        deffered.addCallback(self.activated)
        deffered.addErrback(self.failure)

    def activated(self, ack):
        print 'active'
        self.active = True

    def success(self, ack):
        print 'Success: %s:%s::%s' % (self.host, self.port, ack)

    def failure(self, error):
        print 'Error: %s:%s::%s' % (self.host, self.port, error)

    def connectToNao(self):
        for i in range(0,5):
            try:
                mybroker = ALBroker("mybroker", "0.0.0.0", 0, config.NAO_IP, config.NAO_PORT)
                self.NAOControl = ALProxy("NAOControl")
                break
            except Exception, e:
                print "Connection to NAO not established: ", str(e)
                print "Please check NAO. Automatic retry in 30 seconds."
                wait(30)

if __name__ == '__main__':
    nao_client = NAOClient()
    print 'x'
