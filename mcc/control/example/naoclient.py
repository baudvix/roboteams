import pprint
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import Factory, _InstanceFactory
from twisted.protocols import amp
from mcc.control import command

class RobotProtocol(amp.AMP):

    def update_state(self, state):
        print 'Updating state to %d' % state
        return {'ACK': 'got state'}
    command.UpdateState.responder(update_state)

    def update_position(self, x, y, yaw):
        print 'Updating position (%d, %d, %d)' % (x, y, yaw)
        return {'ACK': 'got position'}
    command.UpdatePosition.responder(update_position)

    def send_map(self, map):
        print 'Updating map '
        pprint.pprint(map)
        return {'ACK': 'got map'}
    command.SendMap.responder(send_map)


class NXTProtocol(RobotProtocol):

    def go_to_point(self,x ,y ):
        print 'Going to Point (%d, %d)' % (x, y)
        return {'ACK': 'got point'}
    command.GoToPoint.responder(go_to_point)


class NAOProtocol(RobotProtocol):

    def nxt_missing(self, nxt_handle, color):
        print 'Searching for NXT #%d, color=%d' % (nxt_handle, color)
        return {'ACK': 'searching'}
    command.NXTMissing.responder(nxt_missing)

    def perform_calibration(self, nxt_handle, color):
        print 'Performing calibration on NXT #%d, color=%d' % (nxt_handle, color)
        return {'ACK': 'try calibration'}
    command.PerformCalibration.responder(perform_calibration)

    def send_path(self, path):
        print 'Follow path'
        pprint.pprint(path)
        return {'ACK': 'follow path'}
    command.SendPath.responder(send_path)
    

class RobotFactory(_InstanceFactory):
    def __init__(self, reactor, instance, deferred):
        _InstanceFactory.__init__(self, reactor, instance, deferred)


class NAOClient():

    def __init__(self, color):
        self.protocol = None
        self.mcc_host = '194.95.174.172'
        self.mcc_port = 5000
        self.listen_port = 6000
        self.color = -1
        self.handle = None
        self.active = False
        self.robot_type = 1 #0:NXT, 1:NAO
        self.factory = None
        self.loop = task.LoopingCall(self.run)
        self.connect()

        reactor.run()
        
    def run(self):
        print 'TODO'

    def connect(self):
        deferred = defer.Deferred()
        if self.protocol is not None:
            self.protocol.transport.loseConnection()
        self.factory = RobotFactory(reactor, NAOProtocol(), deferred)
        connector = reactor.connectTCP(self.mcc_host, self.mcc_port, self.factory)
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

    def activated(self, ACK):
        print 'active'
        self.active = True
        self.listen()
        self.loop.start(1.0)

    def failure(self, error):
        print 'Error: %s:%s\n%s' % (self.mcc_host, self.mcc_port, error)
        self.loop.stop()
    
    def listen(self):
        listener = reactor.listenTCP(self.listen_port, self.factory)
        

if __name__ == '__main__':
    nxt_client = NAOClient(1)
    print 'x'
