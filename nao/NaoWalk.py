__author__ = 'rob'
import time
import math
import motion
from naoqi import ALBroker
from naoqi import ALProxy
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
from mcc.control import command

class NaoWalk():

    # INCOMPLETE AT: walkUpToBall(), include MCC-CALL and delete walkToPosition()

    # Usage description:
    # When the NaoWalk Phase started, call
    #       hasBall()
    #
    # to determine if NAO has the Redball in vision.
    # If not, call
    #       retrieveBall()
    #
    # to find and turn to the ball
    # If NAO has a ball in vision, call
    #       walkUpToBall()
    #
    # NAO will walk up closely to the Redball and call the MCC to
    # request the NXT to move to his next position
    # After the NXT left his initial Position, call
    #       walkToPosition()
    #
    # and NAO makes his few last steps.
    #
    # Repeat this progress until NAO has reached
    # the target area.

    def __init__(self, protocol):
        self.myBroker = ALBroker("myBroker","0.0.0.0",0,"germanopen3.local",9559)
        self.motion = ALProxy("ALMotion")
        self.tracker = ALProxy("ALRedBallTracker")
        self.vision = ALProxy("ALVideoDevice")
        self.tts = ALProxy("ALTextToSpeech")
        self.currentCam = 0
        self.tracker.setWholeBodyOn(False)
        self.tracker.stopTracker()
        self.tracker.startTracker()
        self.ballPosition = []
        self.targetPosition = []
        self.protocol = protocol
        self.target_reached = False
        self.__setTopCamera()

    def __del__(self):
        self.tracker.stopTracker()
        pass

    # determines whether NAO sees a redball or not
    # returns true is he sees one, false if not
    def hasBall(self):
        self.__checkForBall()
        time.sleep(0.5)
        if self.__checkForBall():
            return True
        else :
            return False

    # NAO scans his environment for the redball
    # after calling, NAO either has a redball in vision or there is none in
    # his range of sight.
    # Maybe include MCC-CALL after failure
    def retrieveBall(self):
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        for turnAngle in [0,math.pi/1.8,math.pi/1.8,math.pi/1.8]:
            if turnAngle > 0:
                self.motion.walkTo(0,0,turnAngle)
            if self.hasBall():
                self.__turnToBall()
                return True
            for headPitchAngle in [((math.pi*29)/180),((math.pi*12)/180)]:
                self.motion.angleInterpolation("HeadPitch", headPitchAngle,0.3,True)
                for headYawAngle in [-((math.pi*40)/180),-((math.pi*20)/180),0,((math.pi*20)/180),((math.pi*40)/180)]:
                    self.motion.angleInterpolation("HeadYaw",headYawAngle,0.3,True)
                    time.sleep(0.3)
                    if self.hasBall():
                        self.__turnToBall()
                        return True

    # lets the nao walk close up to the ball
    # Redball in vision is mandatory to call this method!
    # !! NEED TO INCLUDE MCC-CALL TO MOVE NXT TO NEXT POSITION IN LINE 85 !!
    @defer.deferredGenerator
    def walkUpToBall(self):
        ballPosi = self.tracker.getPosition()
        headYawTreshold = ((math.pi*10)/180)
        x = ballPosi[0]/2 + 0.05
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.__turnToBall()
        self.motion.post.walkTo(x,0,0)
        while True:
            headYawAngle = self.motion.getAngles("HeadYaw", False)
            if headYawAngle[0] >= headYawTreshold or headYawAngle[0] <= -headYawTreshold:
                self.motion.stopWalk()
                self.__turnToBall()
                self.walkUpToBall()
                break
            dist = self.__getDistance()
            print dist
            if self.currentCam == 0:
                if dist < 0.75:
                    self.__setBottomCamera()
                    self.motion.angleInterpolation("HeadPitch", -((math.pi*10)/180),0.3,True)
            if self.currentCam == 1:
                if dist < 0.75:
                    self.motion.stopWalk()
                    self.__turnToBall()
                    self.__safePosition()
                    self.__setTopCamera()
                    print 'Waiting for NXT to move'
                    self.tts.say('Waiting for NXT to move')
                    sleepUntilDFRDresult(deferred = self.protocol.callRemote(command.NXTFollowed, handle = 1, nxt_handle = 0, x_axis = 0, y_axis = 0), timeout=60):
                    # deferred = self.protocol.callRemote(command.NXTFollowed, handle = 1, nxt_handle = 0, x_axis = 0, y_axis = 0)
                            
                    deferred.addCallback(self.walkToPosition)
                    #deferred.addErrback(self.waitForNXT)
                    # !!
                    # meldung ans mcc dass nxt weiterlaufen soll
                    # !!
                    
                     # walkToPosition() muss vom mcc aufgerufen werden und hier entfernt werden
                    #self.walkToPosition('bla')
                    
                    break

    def waitForNXT(self, e):
        print 'waiting for NXT to move', e

    # has to be called after walkUpToBall() and the nxt`s gone
    # to the next position to make the last few steps
    def walkToPosition(self, ack):
        print 'Success: %s' %ack
        x = (self.targetPosition[0]/2)
        self.motion.walkTo(x,0,0)
        self.nxt_reached = True

    def __checkForBall(self):
        # for i in range(1,2):
        #     if self.currentCam == 1:
        #         self.__setTopCamera()
        #     else:
        #         self.__setBottomCamera()
        argument = self.tracker.isNewData()
        self.tracker.getPosition()
        return argument

    def __safePosition(self):
        if self.hasBall():
            self.targetPosition = self.tracker.getPosition()
        else :
            return False

    def __setTopCamera(self):
        self.vision.setParam(18,0)
        self.currentCam = 0

    def __setBottomCamera(self):
        self.vision.setParam(18,1)
        self.currentCam = 1

    def __getDistance(self):
        if self.hasBall():
            ballPos = self.tracker.getPosition()
            return math.sqrt(math.pow(ballPos[0],2) + math.pow(ballPos[1],2))

    def __turnToBall(self):
        if not self.hasBall():
            print 'Ball lost'
            # deferred = self.protocol.callRemote(command.BallLost, nao_handle = 1, nxt_handle = 0)
            #moeglicher call ans mcc um retrieveBall aufzurufen
            # deferred.addCallback(self.retrieveBall)
            self.retrieveBall()
            return False
        self.ballPosition = self.tracker.getPosition()
        b = self.ballPosition[1]/self.ballPosition[0]
        z = math.atan(b)
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.motion.walkTo(0,0,z)

    def print_out(self, ack):
        print 'Success: %s' %ack

    def go_to_point(self, x_axis, y_axis):
        self.walkToPosition()
        return {'ack':'got position'}
    command.GoToPoint.responder(go_to_point)

    def followRedBall(self):
        while not self.hasBall():
            print 'retrieve ball'
            self.retrieveBall()
        print 'walk to ball'
        self.walkUpToBall()

def sleepUntilDFRDresult(dfrd, timeout=60):
    '''Hack to make non-blocking deferred waiting for its result or error for
    in `timeout` specified number of seconds, but not to block reactor loop.
    This wrapper *block* the caller until deferred.result or timeout appears.

    >>> dfrd = defer.Deferred() #.addBoth(cbReactorStop)
    >>> sleepUntilDFRDresult(dfrd)       # doctest:+ELLIPSIS
    Exception(u'ERROR sleepUntilDFRDresult server not running for: <Deferred at 0x...> from <doctest
__main__/<module> #L1',)

    >>> startTime = time.time()
    >>> f = lambda: print(sleepUntilDFRDresult(dfrd, timeout=999), 'in:', time.time()-startTime,
'sec.' )
    >>> s1 = reactor.callWhenRunning( f );
    >>> dc2 = reactor.callLater(2, dfrd.callback, 'CALLED')
    >>> dc0 = reactor.callLater(3, reactor.crash); reactor.run()   # doctest:+ELLIPSIS
    WARNING sleepUntilDFRDresult timeout=999 sec. dangerous
    CALLED in: 2.0... sec.
    '''
    if timeout > 600:
        print('WARNING sleepUntilDFRDresult timeout={0} sec. dangerous'.format(timeout) )

    err = None
    if not isinstance(dfrd, defer.Deferred):
        err = 'ERROR sleepUntilDFRDresult dfrd "{0}" not Deferred: '.format(type(dfrd))
    elif not reactor.running:
        err = 'ERROR sleepUntilDFRDresult server not running for: '
    else:
        toTime = time.time() + timeout
        while not dfrd.called and toTime >= time.time():
            try:
                reactor.iterate(0.055)
            except Exception as err:
                pass
            Htime.sleep(0.001)
        if dfrd.called and hasattr(dfrd, 'result'):
            return dfrd.result
    func_name, module_name, line_no = tools.getCallerNameLocation()
    repr_dfrd = '{0} from {2}/{1} #L{3}'.format(dfrd, func_name, module_name, line_no)
    err = Exception( (err or 'ERROR TIMEOUT sleepUntilDFRDresult for: ') + repr_dfrd )
##     print(err)
    return err