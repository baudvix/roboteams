import pprint
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
from mcc.control import command
from nao import NAOCalibration
from nao import NaoWalk
from naoqi import ALProxy
from naoqi import ALBroker
import threading
import time
import sys
from mcc.model import state

NAOControl = None
phase = 0

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
            result = self.factory.robot.calibrate(color)
            return {'handle': nao_handle,'nxt_handle': nxt_handle,'x_axis':result[0],'y_axis':result[1],'yaw': result[2]}
        except NAOCalibration.NXTNotFoundException, e:
            self.factory.protocol.callRemote(command.NXTLost, handle = nao_handle, nxt_handle = nxt_handle)
        except:
            raise
            
    command.PerformCalibration.responder(perform_calibration)

    def send_path(self, nxt_handle, path):
        print 'Following red ball on path'
        pprint.pprint(path)
        for way in path:
            self.factory.robot.walk()
            deferred = self.factory.protocol.callRemote(command.NXTFollowed, handle = self.factory.robot.handle, nxt_handle = nxt_handle, x_axis = way[0], y_axis = way[1])
            deferred.callBack(self.factory.robot.walk())
        return {'ack': 'followed path'}
    command.SendPath.responder(send_path)
    
    def nxt_moved(self, nxt_handle):
        print 'NXT moved - go to point'
        self.factory.robot.walk()
    command.NXTMoved.responder(nxt_moved)

class RobotFactory(_InstanceFactory):
    def __init__(self, reactor, instance, deferred):
        _InstanceFactory.__init__(self, reactor, instance, deferred)
        self.robot = None


class NAO():
    
    def __init__(self, protocol):
        self.handle = None
        self.state = -1
        self.state_lock = threading.Lock()
        self.protocol = protocol
        self.active = False
        self.robot_type = 1
        self.blocked = False
        self.blocked_lock = threading.Lock()
        self.walk_state1 = False
        self.walk_state1_lock = threading.Lock()
        self.walk_state2 = False
        self.walk_state2_lock = threading.Lock()
        self.calibrating = False
        self.calibrating_lock = threading.Lock()
        self.calibration = None
#        self.walking = False
#        self.walking_lock = threading.Lock()
        self.nao_walk = None
        self.nxt_color = None
        self.nxt_color_lock = threading.Lock()
        self.nxt_handle = None
        self.nxt_handle_lock = threading.Lock()
        self.calibration_result = None
#        dispatcher = threading.Thread(target = self.dispatch, args = ())
#        dispatcher.setDaemon(True)
#        dispatcher.start()
#        worker = threading.Thread(target = self.work, args = ())
#        worker.setDaemon(True)
#        worker.start()
        
#    def dispatch(self):
#        while True:
#            
#            while phase == 2:
#                self.blocked_lock.acquire()
#                if self.blocked:
#                    self.walk_state1_lock.acquire()
#                    if self.walk_state1:
#                        if self.walk = None:
#                            self.walk = NaoWalk.NaoWalk()
#                        try:
#                            print 'walkInit'
#                            self.walk.motion.walkInit()
#                            print 'retrieveBall'
#                            self.walk.retrieveBall()
#                            print 'walkUpToBall'
#                            self.walk.walkUpToBall()
#                            self.walk_state2_lock.acquire()
#                            self.walk_state2 = True
#                            self.walk_state2_lock.release()
#                            continue
#                        except NaoWalk.RedBallNotFoundException, e:
#                            print e
#                            self.blocked = False
#                            self.walk_state1 = False
#                            self.walk_state1_lock.release()
#                            self.blocked_lock.release()
#                            deferred = self.protocol.callRemote(command.NXTLost, self.handle, self.nxt_handle)
#                            continue
#                    if self.walk.
#                    
#                self.blocked_lock.release()
#                time.sleep(1)
      
    def calibrate(self, nxt_color):
        while self.state == state.STATE_GUIDED_EXPOLRATION:
            self.calibrating_lock.acquire()
            if self.calibrating:
                self.calibrating_lock.release()
                time.sleep(1)
                continue
            if self.calibration = None:
                self.calibration = NAOCalibration.NAOCalibration()
            try:
                result = self.calibration.performCalibration(nxt_color)
                self.calibrating = False
                self.calibrating_lock.release()
                return result
            except NAOCalibration.NXTNotFoundException, e:
                print e
                raise e
        raise Exception("no calibration in state " + str(self.state))
    
    def walk(self):
        while self.state == state.STATE_NAOWALK:
            self.walk_state1_lock.acquire()
            if self.walk_state1:
                self.walk_state1_lock.release()
                time.sleep(0.5)
                continue
            self.walk_state2_lock.acquire()
            if not self.walk_state2:
                if self.nao_walk:
                    self.nao_walk = NaoWalk.NaoWalk()
                try:
                    print 'walkInit'
                    self.walk.motion.walkInit()
                    print 'retrieveBall'
                    self.walk.retrieveBall()
                    print 'walkUpToBall'
                    self.walk.walkUpToBall()
                    self.walk_state2_lock.acquire()
                    self.walk_state1 = False
                    self.walk_state2 = True
                    self.walk_state1_lock.release()
                    self.walk_state2_lock.release()
                    return
                except NaoWalk.RedBallNotFoundException, e:
                    self.walk_state1 = False
                    self.walk_state1_lock.release()
                    raise e
            else:
                print 'walkToPosition'
                self.walk.walkToPosition()
                self.walk.__setTopCamera()
                self.walk_state2 = False
                self.walk_state1 = True
                self.walk_state2_lock.release()
                self.walk_state1_lock.release()
                continue
                                
        raise Exception("no calibration in state " + str(self.state))
                    
            

class NAOClient():

    def __init__(self):
        self.protocol = None
        self.host = '194.95.174.180'
        self.port = 5000
        self.color = 0
        self.handle = None
        self.active = False
        self.robot_type = 1
#        self.calibration = NAOCalibration()
#        self.walk = NaoWalk()
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
        self.protocol.factory.robot = NAO(protocol)
        deffered = protocol.callRemote(command.Register, robot_type=self.robot_type, rhandle = 4, color=self.color)
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
#        self.connectToNao()
        

    def success(self, ack):
        print 'Success: %s:%s::%s' % (self.host, self.port, ack)

    def failure(self, error):
        print 'Error: %s:%s::%s' % (self.host, self.port, error)

    def connectToNao(self):
        try:
#            for i in range(0,5):
            try:
#                clientbroker = ALBroker("clientbroker", "0.0.0.0", 0, config.NAO_IP, config.NAO_PORT)
                self.NAOControl = ALProxy("NAOControl", config.NAO_IP, config.NAO_PORT)
#                break
            except Exception, e:
                print "Connection to NAO not established: ", str(e)
                print "Please check NAO. Automatic retry in 30 seconds."
                time.sleep(30)
            time.sleep(10)
            print "Send NXTSpotted to MCC"
            deffered = self.protocol.callRemote(command.NXTSpotted(handle = self.handle, nxt_handle = 0))
        except KeyboardInterrupt:
            print "Stopped"
            sys.exit(0)

if __name__ == '__main__':
    print "NAOClient started"
    nao_client = NAOClient()
