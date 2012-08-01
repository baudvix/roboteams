from twisted.protocols import amp
from twisted.internet import reactor, task, defer
from twisted.internet.protocol import Factory
import sys
sys.path.append("../..")
from mcc.control import command
from mcc.model import robot


class MCCProtocol(amp.AMP):
    def __init__(self):
        amp.AMP.__init__(self)
        self.factory = None

    def register(self, robot_type, rhandle, color=None):
        print 'NEW robot: type=%d color=%d' % (robot_type, color)
        if robot_type == robot.NXT_TYPE:
            self.factory.robots.append(robot.RobotNXT(self.factory.last_handle, self, color))
        else:
            self.factory.robots.append(robot.RobotNAO(self.factory.last_handle, self))
        self.factory.last_handle += 1
        return {'rhandle': rhandle, 'handle': (self.factory.last_handle - 1)}
    command.Register.responder(register)

    def activate(self, handle):
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo.active = True
                print '#%d activated' % handle
                #self.callRemote(command.GoToPoint, x=0, y=50)
                return {'ACK': 'got activate'}
        raise command.CommandHandleError('No robot with handle')
    command.Activate.responder(activate)

    def nxt_calibrated(self, handle, nxt_handle, x, y, yaw):
        print '#%d NXT calibrated #%d (%d, %d, %d)' % (handle, nxt_handle, x,
                                                       y, yaw)
        return {'ACK': 'got calibrated'}
    command.NXTCalibrated.responder(nxt_calibrated)

    def nxt_spotted(self, handle, nxt_handle):
        print '#%d Roboter spotted NXT #%d' % ( handle, nxt_handle)
        return {'ACK': 'got spotted'}
    command.NXTSpotted.responder(nxt_spotted)

    def send_data(self,handle, point_tag, x, y, yaw):
        print '#%d Send data %d: (%d, %d, %d)' % (handle, point_tag, x, y,
                                                  yaw)
        return{'ACK': 'got data'}
    command.SendData.responder(send_data)

    def arrived_point(self, handle, x, y):
        print '#%d Arrived at (%d. %d)' % (handle, x, y)
        return {'ACK': 'got arrival'}
    command.ArrivedPoint.responder(arrived_point)

    def connectionLost(self, reason):
        for robo in self.factory.robots:
            if robo.connection == self:
                robo.active = False
                print 'Connection Lost to robo %d ' % robo.handle

class MCCFactory(Factory):

    protocol = MCCProtocol

    def __init__(self, reactor, instance, deferred):
        self.last_handle = 0
        self.robots = []
        #TODO start a thread for heavy calculation
        #TODO start a thread for view


class MCCServer(object):

    def __init__(self):
        self.protocol = None
        self.host = 'localhost'
        self.port = 5000
        self.robots = None
        self.listen()
        loop = task.LoopingCall(self.run)
        loop.start(30.0)
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