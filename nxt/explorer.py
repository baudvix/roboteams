#!/usr/bin/env python
# -*- coding: utf-8 -*-
OFFLINE = False

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
from nxt.locator import Method

if OFFLINE == False:
    from nxt.locator import find_one_brick
else:
    from pseudobrick import find_one_brick

MAC = ["00:16:53:10:49:4D", "00:16:53:10:48:E7", "00:16:53:10:48:F3"]
GRAD2CM = 17.59/360.0
CM2GRAD = 360.0/17.59

def berechnePunkt(ausrichtung, entfernung, standort={'x':0.0, 'y':0.0}):
    return {'x': standort['x'] + entfernung*GRAD2CM*math.cos(ausrichtung*(math.pi/180.0)), 
            'y': standort['y'] + entfernung*GRAD2CM*math.sin(ausrichtung*(math.pi/180.0))}


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

    def __init__(self):
        self.factory = None

    def go_to_point(self,x ,y ):
        dbg_print('Going to Point ('+str(x)+','+str(y)+')',2)
        if self.factory.robots[0].go_to_point(x,y):#TODO: rhandle von NXT benoetigt
            self.factory.robots[0].position_lock.acquire()
            self.callRemote(command.ArrivedPoint, 
                            handle=self.factory.robots[0].handle, #FIXME: eigen Standort an Protokoll übergeben
                            x=x,#self.factory.robots[0].position['x'],#FIXME: eigen Standort an Protokoll übergeben
                            y=y)#self.factory.robots[0].position['y']) #FIXME: eigen Standort an Protokoll übergeben
            self.factory.robots[0].position_lock.release()
            return {'ACK': 'got point'}
        else:#FIXME: Exception 
            #FIXME: roboter.go_to_point() returned false
            self.factory.robots[0].position_lock.acquire()
            self.callRemote(command.ArrivedPoint, 
                            handle=self.factory.robots[0].handle,
                            x=self.factory.robots[0].position['x'],
                            y=self.factory.robots[0].position['y'])
            self.factory.robots[0].position_lock.release()
            return {'ACK': 'not'}
    command.GoToPoint.responder(go_to_point)

class RobotFactory(_InstanceFactory):
    def __init__(self, reactor, instance, deferred, anzahl):
        _InstanceFactory.__init__(self, reactor, instance, deferred)
        self.anzahl = anzahl
        self.robots = [None]*anzahl


class Explorer():
    '''Die Explorer-Klasse stellt die Verbindung zu einem durch seine MAC-Adresse identifizierten NXT her und stellt die Funktionalität zur Steuerung bereit.'''
    #FIXME: trennen von blosser Steuerung und Logik
    def __init__(self, mac, identitaet, color, outbox=5, inbox=1):
        self.brick = find_one_brick(host=mac, method=Method(usb=True, bluetooth=True))
        self.color = color# FIXME: potentiell unnoetig
        self.ausrichtung = 90; # 0 - 359 Grad; 0 Osten, 90 Norden, 180 Westen, 270 Sueden 
        self.identitaet = identitaet
        self.phase = 0
        self.status = None
        self.status_lock = threading.Lock()
        self.handle = None
        self.active = False
        self.blockiert = False
        self.blockiert_lock = threading.Lock()
        self.abbruch = True
        self.abbruch_lock = threading.Lock()
        self.robot_type = 0
        self.message_id = 0
        self.position_lock = threading.Lock()
        self.position = {'x': 0.0,'y': 0.0}
        self.outbox = outbox
        self.inbox = 10 + inbox 
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
        time.sleep(4.0)
        self.blockiert_lock.acquire()
        self.blockiert = False
        self.blockiert_lock.release()   
        
    def go_forward(self, distance):
        self.send_message(message='1,'+str(distance))
        
    def go_back(self, distance):
        self.send_message(message='2,'+str(distance))
        self.position_lock.acquire()
        self.position = berechnePunkt(self.ausrichtung, -1*distance*360, self.position)
        self.position_lock.release()
    
    def go_to_point(self, x, y):
        self.stop()
        self.position_lock.acquire()
        vektor = berechneVektor(self.position, {'x': x, 'y': y})
        self.position_lock.release()
        self.blockiert_lock.acquire()
        self.blockiert = True
        self.blockiert_lock.release()
        if vektor['winkel'] > 90 and vektor['winkel'] <= 270:
            self.turnleft(vektor['winkel'])
        else:
            self.turnright(vektor['winkel'])
        self.blockiert_lock.acquire()
        self.blockiert = True
        self.blockiert_lock.release()
        self.go_forward(int(round(vektor['entfernung'])))
        self.blockiert_lock.acquire()
        self.blockiert_lock.release()
        self.status_lock.acquire()
        if self.status == 'arrived':
            self.status_lock.release()
            self.position_lock.acquire()
            self.position = {'x': x, 'y': y}
            self.position_lock.release()
            return True
        elif self.status == 'hit':
            self.status_lock.release()
            self.position_lock.acquire()
            self.position = {'x': x, 'y': y}
            self.position_lock.release()
            return False
        else: # potentiell Exception, oder ziel gefunden
            self.status_lock.release()
            return False
        
    
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
                state %= 3
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
            intervall = random.choice([60.0])
            time.sleep(intervall)
            if self.phase == 0:
                self.abbruch_lock.acquire()
                self.abbruch = True
                self.abbruch_lock.release()
                self.stop()
                print "exploration_cancel - abbruch= True gewartet f�r %d sek" % intervall
    
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

    def recv_message(self):
        t = self.brick.message_read(self.inbox, self.inbox, True)
        dbg_print(t,6)
        return t 

    def dispatch(self):       
        dbg_print("run dispatch",2)
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
                    if int(csv[0]) == 1: #nach Zeitintervall 500ms update_position (Entfernung)
                        dbg_print("Update: "+str(csv[1])+" Einheiten gefahren") 
                        #print berechnePunkt(self.ausrichtung, csv[1], self.position)#TODO an MCC
                    elif int(csv[0]) == 2: #kollision update_position (Entfernung)
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                        self.status_lock.acquire()
                        self.status = 'hit'
                        self.status_lock.release()
                        dbg_print("Kollision: "+str(csv[1])+" Einheiten gefahren") 
                        self.position_lock.acquire()
                        self.position = berechnePunkt(self.ausrichtung, csv[1], self.position) #TODO an MCC
                        self.position_lock.release()
                        dbg_print(str(self.position))
                    elif int(csv[0]) == 3: #strecke ohne vorkommnisse abgefahren
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                        self.status_lock.acquire()
                        self.status = 'arrived'
                        self.status_lock.release()
                        self.position_lock.acquire()
                        self.position = berechnePunkt(self.ausrichtung, int(csv[1]), self.position) #TODO an MCC
                        self.position_lock.release()
                        dbg_print(str(csv[1])+" Einheiten gefahren") 
                    elif int(csv[0]) == 4: #beendet rueckwaerts und drehen
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                        dbg_print("Drehen oder Zurueck") 
                    elif int(csv[0]) == 9: #ziel gefunden gleich kommt t
                        dbg_print("Ziel gefunden") 
    
                else:
                    dbg_print('Falscher Nachrichtentyp')
            except:
                pass
            count += 1  
    
    def work(self):
        time.sleep(3.0)
        t = threading.Thread(target=self.exploration_cancel, args=())
        t.setDaemon(True)
        t.start()
        while(True):
            time.sleep(1.0)
            if self.handle == None:
                continue
            self.abbruch_lock.acquire()
            if self.abbruch:
                self.abbruch = False
                self.abbruch_lock.release()
                if self.phase == 0:
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
        self.factory = RobotFactory(reactor, NXTProtocol(), deferred, self.anzahl)
        reactor.connectTCP(self.host, self.port, self.factory)
        deferred.addCallback(self.connected)
        deferred.addErrback(self.failure)

    def connected(self, protocol):
        self.protocol = protocol
        self.protocol.factory = self.factory
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
