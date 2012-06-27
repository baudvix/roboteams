import pprint
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
from mcc.control import command


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

    def perform_calibration(self, nxt_handle, color):
        print 'Performing calibration on NXT #%d, color=%d' % (nxt_handle, color)
        return {'ack': 'try calibration'}
    command.PerformCalibration.responder(perform_calibration)

    def send_path(self, path):
        print 'Follow path'
        pprint.pprint(path)
        return {'ack': 'follow path'}
    command.SendPath.responder(send_path)


class RobotFactory(_InstanceFactory):
    def __init__(self, reactor, instance, deferred):
        _InstanceFactory.__init__(self, reactor, instance, deferred)


class NAOClient():

    def __init__(self):
        self.protocol = None
        self.host = 'localhost'
        self.port = 5000
        self.color = 0
        self.handle = None
        self.active = False
        self.robot_type = 1
        self.connect()
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

if __name__ == '__main__':
    nao_client = NAOClient()
    print 'x'
