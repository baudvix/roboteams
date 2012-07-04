#!/usr/bin/env python
# -*- coding: latin-1 -*-
import random
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


TIMEOFFSET = 2.0 #zeit bis zum nochmaligen Senden
MAC = ["00:16:53:10:49:4D", "00:16:53:10:48:E7", "00:16:53:10:48:F3"]
GRAD2CM = 17.59/360.0
CM2GRAD = 360.0/17.59

def berechnePunkt(ausrichtung, entfernung, standort={'x':0.0, 'y':0.0}):
    pos = {'x':0.0, 'y':0.0}
    pos['x'] = standort['x'] + entfernung*GRAD2CM*math.cos(ausrichtung*(math.pi/180.0))
    pos['y'] = standort['y'] + entfernung*GRAD2CM*math.sin(ausrichtung*(math.pi/180.0))
    return pos

def berechneVektor(standort={'x':0.0, 'y':0.0}, ziel={'x': 0.0, 'y': 0.0}):
    relativ_ziel = {'x': ziel['x']-standort['x'],'y': ziel['y']-standort['y']}
    entfernung = math.sqrt(relativ_ziel['x']**2+relativ_ziel['y']**2)
    if relativ_ziel['x'] == 0: 
        winkel = 0
    elif relativ_ziel['x'] < 0:
        winkel = math.atan(relativ_ziel['y']/relativ_ziel['x'])*(180.0/math.pi)+180
    else:
        winkel = math.atan(relativ_ziel['y']/relativ_ziel['x'])*(180.0/math.pi)+360
    return {'winkel': winkel%360, 'entfernung': entfernung*CM2GRAD}

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
        self.blockiert_lock = threading.Lock()
        self.abbruch = True
        self.abbruch_lock = threading.Lock()
        self.robot_type = 0
        self.message_id = 0
        self.position = {'x': 0.0,'y': 0.0}
        self.outbox = outbox
        self.inbox = 10 + inbox
        self.timelist = []
        self.timelist_lock = threading.Lock()     
        self.start_app("explorer.rxe")
        random.seed()
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
       
    def stop(self):
        self.send_message(message='0,0')   
        
    def go_forward(self, distance):
        self.send_message(message='1,'+str(distance))
        
    def go_back(self, distance):
        self.send_message(message='2,'+str(distance))
        t = self.berechnePunkt(self.ausrichtung, -1*distance*360, self.position)
        self.position = t
        print self.position
    
    def exploration_simple(self):
        state = 0
        while(True):
            self.abbruch_lock.acquire()
            if self.abbruch:
                self.abbruch_lock.release()
                break
            self.abbruch_lock.release()
            self.blockiert_lock.acquire()
            if not self.blockiert:
                self.blockiert = True
                self.blockiert_lock.release()
                print "exploration_simple - state=%d" % state
                
                if state == 0:
                    self.go_forward(0)
                elif state == 1:
                    self.go_back(1)
                elif state == 2:
                    linksrechts = random.choice([0,1]) #0=links || 1=rechts
                    grad = random.randint(30, 160) # 30 - 160
                    if linksrechts == 0:
                        self.turnleft(grad)
                    else:
                        self.turnright(grad)
                state += 1
                state %= 2
            else:
                self.blockiert_lock.release()       
                
    def exploration_circle(self): 
        while(True):
            self.abbruch_lock.acquire()
            if self.abbruch:
                self.abbruch_lock.release()
                break
            self.abbruch_lock.release()
            print "exploration_circle"
            time.sleep(1.0)
    
    def exploration_radar(self):
        while(True):
            self.abbruch_lock.acquire()
            if self.abbruch:
                self.abbruch_lock.release()
                break
            self.abbruch_lock.release()
            print "exploration_radar"
            time.sleep(1.0)
    
    def exploration_cancel(self):
        while(True):
            intervall = random.choice([5.0])
            time.sleep(intervall)
            self.abbruch_lock.acquire()
            self.abbruch = True
            self.abbruch_lock.release()
            self.stop()
            self.timelist_lock.acquire()
            self.timelist_access('l', 0)
            self.timelist_lock.release()
            print "exploration_cancel - abbruch= True gewartet für %d sek" % intervall
    
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
        tstr = typ+";"+str(ident)+";"+message
        dbg_print(tstr, 6)
        self.brick.message_write(self.outbox, tstr)
        if typ != 'a':
            dbg_print('timelist.append: '+str((time.time(), typ, ident, message)),3)
            self.timelist.append((time.time(), typ, ident, message))

    def recv_message(self):
        t = self.brick.message_read(self.inbox, self.inbox, True)
        dbg_print(t,6)
        return t 

    def timelist_access(self, choose, ident):
        dbg_print("timelist_access timelist_lock choose="+str(choose)+" ident="+str(ident),3)
        if choose == 'r' or choose == 'a':
            for tupel in self.timelist:
                if tupel[2] == ident:
                    self.timelist.remove(tupel)
        elif choose == 't':         
            for tupel in self.timelist:
                if tupel[0]+TIMEOFFSET <= time.time():
                    self.timelist.remove(tupel)
                    self.send_message(message=tupel[3], typ=tupel[1], ident=tupel[2])
        elif choose == 'l':         
            self.timelist = []
        dbg_print("timelist: "+str(self.timelist),3)
        dbg_print("timelist_access unlock choose="+str(choose)+" ident="+str(ident),3)

    def dispatch(self):       
        dbg_print("run dispatch",2)
        dbg_print("run timer",2)
        t = threading.Thread(target=self.timer, args=())
        t.setDaemon(True)
        t.start()
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
                    self.send_message(typ='r', ident=ident, message='resp')
                    # irgendetwas mit payload machen
                    csv = payload.split(',') # payload = event, entfernung, sensor(optional)
                    if str(csv[0]) == 'p': #nach Zeitintervall 500ms update_position (Entfernung)
                        print "%d Einheiten gefahren" % csv[1]
                        print berechnePunkt(self.ausrichtung, csv[1], self.position)#TODO an MCC
                    elif str(csv[0]) == 'h': #kollision update_position (Entfernung)
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                        print "Kollision: %d Einheiten gefahren" % csv[1]
                        t = berechnePunkt(self.ausrichtung, csv[1], self.position) #TODO an MCC
                        self.position = t
                        print self.position
                    elif str(csv[0]) == 't': #strecke ohne vorkommnisse abgefahren
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                        print "%d Einheiten gefahren" % csv[1]
                        t = berechnePunkt(self.ausrichtung, csv[1], self.position) #TODO an MCC
                        self.position = t
                        print self.position
                    elif str(csv[0]) == 'f': #ziel gefunden gleich kommt t
                        print "Ziel gefunden"
    
                elif typ == 'r':
                    self.timelist_lock.acquire()
                    self.timelist_access(typ, ident)
                    self.timelist_lock.release()
                    self.send_message(typ='a', ident=ident, message='ack')

                elif typ == 'a':
                    self.timelist_lock.acquire()
                    self.timelist_access(typ, ident)
                    self.timelist_lock.release()
                else:
                    dbg_print('Falscher Nachrichtentyp')
            except:
                pass
            count += 1
            
    def timer(self):
        while(True):
            time.sleep(1.0)
            self.timelist_lock.acquire()
            self.timelist_access('t', 0)
            self.timelist_lock.release()    
    
    def work(self):
        time.sleep(3.0)
        t = threading.Thread(target=self.exploration_cancel, args=())
        t.setDaemon(True)
        t.start()
        while(True):
            time.sleep(1.0)
            if self.handle == None:
                continue
            state = 0 #FIXME
            self.abbruch_lock.acquire()
            if self.abbruch:
                self.abbruch = False
                self.abbruch_lock.release()
                if state == 0:
                    algo = random.choice([0])
                    if algo == 0:           
                        self.exploration_simple() #blockierender Aufruf
                    elif algo == 1:
                        self.exploration_radar() #blockierender Aufruf
                    elif algo == 2:
                        self.exploration_circle() #blockierender Aufruf
            else:
                self.abbruch_lock.release()
                        
                
    
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
        reactor.connectTCP(self.host, self.port, self.factory)
        deferred.addCallback(self.connected)
        deferred.addErrback(self.failure)

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
