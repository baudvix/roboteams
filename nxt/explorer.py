#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
import time
import threading
import math
sys.path.append('..')
import pprint
from twisted.internet import reactor, defer, task
from twisted.internet.protocol import Factory, _InstanceFactory
from twisted.protocols import amp
from mcc.control import command

from nxt_debug import dbg_print, DEBUGLEVEL
from nxt.brick import FileFinder
from nxt.locator import find_one_brick, Method

TIMEOFFSET = 3.0 #zeit bis zum nochmaligen Senden
MAC = ["00:16:53:10:49:4D", "00:16:53:10:48:E7", "00:16:53:10:48:F3"]
GRAD2CM = 17.59/360.0
CM2GRAD = 360.0/17.59

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

class RobotFactory(_InstanceFactory):    
    def __init__(self, reactor, instance, deferred, anzahl):
        _InstanceFactory.__init__(self, reactor, instance, deferred)
        self.anzahl = anzahl
        self.robots = [None]*anzahl


class Explorer():
    def __init__(self, mac, identitaet, color, outbox=5, inbox=1):
        self.brick = find_one_brick(host=mac, method=Method(usb=True, bluetooth=True))
        self.color = color
        self.ausrichtung = 90; # 0 - 359 Grad; 0 Osten, 90 Norden, 180 Westen, 270 Sueden 
        self.identitaet = identitaet
        self.handle = None
        self.active = False
        self.blockiert = False
        self.abbruch = False
        self.robot_type = 0
        self.message_id = 0
        self.position = {'x':0,'y':0}
        self.outbox = outbox
        self.inbox = 10 + inbox
        self.timelist = []
        self.lock = threading.Lock()     
        self.start_app("explorer.rxe")
        dispatcher = threading.Thread(target=self.dispatch, args=())
        dispatcher.setDaemon(True)
        dispatcher.start()
        worker = threading.Thread(target=self.work, args=())
        worker.setDaemon(False)
        worker.start()
        
    def __del__(self):
        pass
    
    def event(self, message):
        pass
    
    def turnright(self, degrees):
        self.send_message(message='4,'+str(degrees))
        self.ausrichtung+=degrees
        self.ausrichtung%=360
    
    def turnleft(self,  degrees):    
        self.send_message(message='3,'+str(degrees))
        if self.ausrichtung < degrees:
            self.ausrichtung+=360
        
        self.ausrichtung-=degrees
        self.ausrichtung%=360
        
    def go_forward(self, distance):
        self.send_message(message='1,'+str(distance))
        
    def go_back(self, distance):
        self.send_message(message='2,'+str(distance))
    
    def exploration_simple(self):
        first = True
        while(not self.abbruch):
            if not self.blockiert:
                self.blockiert = True
                if not first:
                    self.go_back(1)
                    linksrechts = 0 #0=links || 1=rechts
                    grad = 90 # 30 - 160
                    if linksrechts == 0:
                        self.turnleft(grad)
                    else:
                        self.turnright(grad)
                first = False
                self.go_forward(0)
    
    def exploration_circle(self): 
        pass
    
    def exploration_radar(self):
        pass
    
    def exploration_cancel(self):
        self.abbruch = True
    
    def berechnePunkt(self, ausrichtung, entfernung, standort={'x':0, 'y':0}):
        pos = {'x':0, 'y':0}
        pos['x'] = standort['x'] + entfernung*GRAD2CM*math.cos(ausrichtung*(math.pi/180.0))
        pos['y'] = standort['y'] + entfernung*GRAD2CM*math.sin(ausrichtung*(math.pi/180.0))
        return pos
    
    def find_programs(self):
        ff = FileFinder(self.brick, "*.rxe")
        for f in ff:
            print(f)
    
    def start_app(self, app):
        self.brick.start_program(app)
        
    def send_message(self, message = '', typ = 'm', ident = 99):
        if typ == 'm' and ident == 99:
            self.message_id += 1
            self.message_id %= 10
            ident = self.message_id
        self.brick.message_write(self.outbox, typ+";"+str(ident)+";"+message)
        if typ != 'a':
            dbg_print('timelist.append: '+str((time.time(), typ, ident, message)),3)
            self.timelist.append((time.time(), typ, ident, message))

    def recv_message(self):
        t = self.brick.message_read(self.inbox, self.inbox, True)
        dbg_print(t,6)
        return t 

    def timelist_access(self, choose, ident):
        dbg_print("timelist_access lock choose="+str(choose)+" ident="+str(ident),3)
        if choose == 'r' or choose == 'a':
            for tupel in self.timelist:
                if tupel[2] == ident:
                    self.timelist.remove(tupel)
        elif choose == 't':         
            for tupel in self.timelist:
                if tupel[0]+TIMEOFFSET <= time.time():
                    self.timelist.remove(tupel)
                    self.send_message(message=tupel[3], typ=tupel[1], ident=tupel[2])
        dbg_print("timelist: "+str(self.timelist),3)
        dbg_print("timelist_access unlock choose="+str(choose)+" ident="+str(ident),3)

    def dispatch(self):       
        dbg_print("run dispatch",2)
        dbg_print("run timer",2)
        t = threading.Thread(target=self.timer, args=())
        t.setDaemon(True)
        t.start()
        dbg_print("BT-Empfang",1)
        count = 0
        while(True):
            if count%100000 == 0:
                dbg_print("dispatch() - #"+str(count),3)
            try:
                _, message = self.recv_message()
                dbg_print("message: "+str(message),9)
                try: 
                    typ, t_id, payload = str(message).split(';')
                    ident = int(t_id)
                except:
                    dbg_print("message-parsing-error: falsches Format")
                dbg_print("typ="+str(typ)+" ident="+str(t_id)+" msg="+str(payload),4)   
                if typ == 'm':
                    # irgendetwas mit payload machen
                    csv = payload.split(',') # payload = event, entfernung, sensor(optional)
                    if csv[0] == 's': #nach Zeitintervall 500ms update_position (Entfernung)
                        print "%d Einheiten gefahren" % csv[1]
                    elif csv[0] == 'h': #kollision update_position (Entfernung)
                        self.blockiert = False
                        print "Kollision: %d Einheiten gefahren" % csv[1]
                    elif csv[0] == 't': #strecke ohne vorkommnisse abgefahren
                        print "%d Einheiten gefahren" % csv[1]
                    elif csv[0] == 'f': #ziel gefunden gleich kommt t
                        print "Ziel gefunden"
                    self.send_message(typ='r', ident=ident, message='resp')
                    
                elif typ == 'r':
                    self.lock.acquire()
                    self.timelist_access(typ, ident)
                    self.lock.release()
                    self.send_message(typ='a', ident=ident, message='ack')

                elif typ == 'a':
                    self.lock.acquire()
                    self.timelist_access(typ, ident)
                    self.lock.release()
                else:
                    dbg_print('Falscher Nachrichtentyp')
            except:
                pass
            count += 1
            
    def timer(self):
        while(True):
            time.sleep(3.0)
            self.lock.acquire()
            self.timelist_access('t', 0)
            self.lock.release()    
    
    def work(self):
        while(True):
            time.sleep(1.0)
            if self.handle == None:
                continue
            state = 0#FIXME  
            if not self.blockiert:
                if state == 0:
                    algo = 0
                    explorationsintervall = 10.0
                    if algo == 0:           
                        self.exploration_simple()
                    elif algo == 1:
                        self.exploration_radar()
                    elif algo == 2:
                        self.exploration_circle()
                    expl_abbr = threading.Timer(explorationsintervall,self.exploration_cancel())
                    expl_abbr.start()
                        
                
    
class NXTClient():

    def __init__(self, anzahl=1):
        self.protocol = None
        self.host = 'localhost'
        self.port = 5000
        self.anzahl = anzahl
        self.factory = None
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
        self.factory = RobotFactory(reactor, RobotProtocol(), deferred, self.anzahl)
        #connector = reactor.connectTCP(self.host, self.port, factory)
        reactor.connectTCP(self.host, self.port, self.factory)
        deferred.addCallback(self.connected)
        deferred.addErrback(self.failure)
        #return deferred

    def connected(self, protocol):
        self.protocol = protocol
        print 'connected to mcc'
        for bot in range(self.anzahl):
            try:
                self.factory.robots[bot] = Explorer(MAC[bot], bot, bot+1,5+bot,1+bot)
            except:
                print "Bot %s nicht gefunden" % MAC[bot]
                self.factory.robots[bot] = None
            if self.factory.robots[bot] != None:
                deffered = protocol.callRemote(command.Register, 
                                               robot_type=self.factory.robots[bot].robot_type, 
                                               color=self.factory.robots[bot].color, rhandle=bot)
                deffered.addCallback(self.activate)
                deffered.addErrback(self.failure)

    def activate(self, handle):
        self.factory.robots[handle['rhandle']].handle = handle['handle']
        print "handle=%s" % (self.factory.robots[handle['rhandle']].handle)
        deffered = self.protocol.callRemote(command.Activate, handle=self.factory.robots[handle['rhandle']].handle)
        deffered.addCallback(self.activated)
        deffered.addErrback(self.failure)

    def activated(self, ACK):
        print 'active'
        self.active = True

    def failure(self, error):
        print 'Error: %s:%s\n%s' % (self.host, self.port, error)

if __name__ == '__main__' and DEBUGLEVEL > 0:
    dbg_print("__main__ start")
    test = NXTClient(1)
    dbg_print("__main__ fertig")
