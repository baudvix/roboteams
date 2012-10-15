import pprint
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
from mcc.control import command
from nao import NAOCalibration
from nao import NaoWalk, config
from naoqi import ALProxy
from naoqi import ALBroker
import threading
import time
import sys
from mcc.model import state

NAOControl = None
phase = 0

walk = NaoWalk.NaoWalk()

walk.motion.walkInit()
print 'retrieveBall'
walk.retrieveBall()
print 'walkUpToBall'
walk.walkUpToBall()