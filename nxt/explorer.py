#!/usr/bin/env python

OFFLINE = False
phase = 0 # TODO phase von mcc

#TODO: calibrating via ultrasonic distance and engine distance
#TODO: dividing into logical explorer and physical explorer 
#TODO: communication with MCC (callback functions)
#TODO: commenting functions
#TODO: dodges in expl-algos...

import random
import sys
import time
import threading
import math
sys.path.append('..')
import pprint
from mcc.model import map
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
GRAD2CM = 17.59 / 360.0
CM2GRAD = 360.0 / 17.59

def berechnePunkt(ausrichtung, entfernung, standort = {'x':0.0, 'y':0.0}):
    return {'x': standort['x'] + entfernung * GRAD2CM * math.cos(ausrichtung * (math.pi / 180.0)),
            'y': standort['y'] + entfernung * GRAD2CM * math.sin(ausrichtung * (math.pi / 180.0))}


def berechneVektor(standort = {'x':0.0, 'y':0.0}, ziel = {'x': 0.0, 'y': 0.0}):
    relativ_ziel = {'x': ziel['x'] - standort['x'], 'y': ziel['y'] - standort['y']}
    entfernung = math.sqrt(relativ_ziel['x'] ** 2 + relativ_ziel['y'] ** 2)
    if relativ_ziel['x'] == 0:
        winkel = 0
    elif relativ_ziel['x'] < 0:
        winkel = math.atan(relativ_ziel['y'] / relativ_ziel['x']) * (180.0 / math.pi) + 180
    else:
        winkel = math.atan(relativ_ziel['y'] / relativ_ziel['x']) * (180.0 / math.pi) + 360
    return {'winkel': winkel % 360, 'entfernung': entfernung}

class RobotProtocol(amp.AMP):

    def update_state(self, state):
        print 'Updating state to %d' % state
        return {'ACK': 'got state'}
    command.UpdateState.responder(update_state)

    def update_position(self, handle, x_axis, y_axis, yaw):
        print 'Updating position (%d, %d, %d)' % (x_axis, y_axis, yaw)
        return {'ack': 'got position'}
    command.UpdatePosition.responder(update_position)

    def send_map(self, map):
        print 'Updating map '
        pprint.pprint(map)
        return {'ACK': 'got map'}
    command.SendMap.responder(send_map)

class NXTProtocol(RobotProtocol):

    def __init__(self):
        self.factory = None

    def go_to_point(self, handle, x_axis , y_axis):
        dbg_print('Going to Point (' + str(x_axis) + ',' + str(y_axis) + ')', 2)
        if self.factory.robots[handle].go_to_point(x_axis, y_axis):
            self.factory.robots[handle].position_lock.acquire()
            self.callRemote(command.ArrivedPoint,
                            handle = self.factory.robots[handle].handle, 
                            x_axis = self.factory.robots[handle].position['x_axis'],
                            y_axis = self.factory.robots[handle].position['y_axis'])
            self.factory.robots[handle].position_lock.release()
            return {'ACK': 'got point'}
        else:#FIXME: Exception 
            self.factory.robots[handle].position_lock.acquire()
            self.callRemote(command.ArrivedPoint,
                            handle = self.factory.robots[handle].handle,
                            x_axis = self.factory.robots[handle].position['x_axis'],
                            y_axis = self.factory.robots[handle].position['y_axis'])
            self.factory.robots[handle].position_lock.release()
            return {'ACK': 'not'}
    command.GoToPoint.responder(go_to_point)

    def update_state(self, state):
        print 'Updating state to %d' % state
        phase = state
        return {'ACK': 'got state'}
    command.UpdateState.responder(update_state)

    def update_position(self, handle, x_axis, y_axis, yaw):
        print 'Updating position (%d, %d, %d)' % (x_axis, y_axis, yaw)
        self.factory.robots[handle].position_lock.acquire()
        self.factory.robots[handle].position['x'] = x_axis
        self.factory.robots[handle].position['y'] = y_axis
        self.factory.robots[handle].ausrichtung = yaw
        self.factory.robots[handle].position_lock.release()
        return {'ack': 'got position'}
    command.UpdatePosition.responder(update_position)

    def send_map(self, map):
        print 'Updating map '
        pprint.pprint(map)
        return {'ACK': 'got map'}
    command.SendMap.responder(send_map)

class RobotFactory(_InstanceFactory):
    def __init__(self, reactor, instance, deferred, anzahl):
        _InstanceFactory.__init__(self, reactor, instance, deferred)
        self.anzahl = anzahl
        self.robots = [None] * anzahl


class Explorer():
    '''Die Explorer-Klasse stellt die Verbindung zu einem durch seine MAC-Adresse identifizierten NXT her und stellt die Funktionalitaet zur Steuerung bereit.'''
    #FIXME: trennen von blosser Steuerung und Logik
    def __init__(self, mac, protokoll, identitaet, color, outbox = 5, inbox = 1):
        self.brick = find_one_brick(host = mac, method = Method(usb = True, bluetooth = True))
        self.color = color# FIXME: potentiell unnoetig
        self.ausrichtung = 90; # 0 - 359 Grad; 0 Osten, 90 Norden, 180 Westen, 270 Sueden
        self.calibrationFactor = 1 
        self.protokoll = protokoll
        self.identitaet = identitaet
        self.status = -1
        self.status_lock = threading.Lock()
        self.handle = None
        self.active = False
        self.blockiert = False
        self.blockiert_lock = threading.Lock()
        self.payload = 0
        self.payload_lock = threading.Lock()
        self.abbruch = True
        self.abbruch_lock = threading.Lock()
        self.robot_type = 0
        self.message_id = 0
        self.position_lock = threading.Lock()
        self.position = {'x': 0.0, 'y': 0.0}
        self.outbox = outbox
        self.inbox = 10 + inbox
        self.start_app("explorer.rxe")
        random.seed()
        dispatcher = threading.Thread(target = self.dispatch, args = ())
        dispatcher.setDaemon(True)
        dispatcher.start()
        worker = threading.Thread(target = self.work, args = ())
        worker.setDaemon(False)
        worker.start()

    def __del__(self):
        pass

    def event(self, message):
        pass

    def turnright(self, degrees):
        self.send_message(message = '4,' + str(degrees))
        self.position_lock.acquire()
        self.ausrichtung += degrees
        self.ausrichtung %= 360
        self.position_lock.release()

    def turnleft(self, degrees):
        self.send_message(message = '3,' + str(degrees))
        self.position_lock.acquire()
        if self.ausrichtung < degrees:
            self.ausrichtung += 360

        self.ausrichtung -= degrees
        self.ausrichtung %= 360
        self.position_lock.release()

    def stop(self):
        self.send_message(message = '0,0')
        time.sleep(2.0)
        self.blockiert_lock.acquire()
        self.blockiert = False
        self.blockiert_lock.release()

    def go_forward(self, distance):
        self.send_message(message = '1,' + str(int(round(distance*CM2GRAD*self.calibrationFactor))))

    def go_back(self, distance):
        self.send_message(message = '2,' + str(int(round(distance*self.calibrationFactor))))#*CM2GRAD))))
        self.position_lock.acquire()
        self.position = berechnePunkt(self.ausrichtung, -1 * distance, self.position)
        self.position_lock.release()

    def go_to_point(self, x, y):
        self.stop()
        self.position_lock.acquire()
        vektor = berechneVektor(self.position, {'x': x, 'y': y})
        self.position_lock.release()
        while(True):
            self.blockiert_lock.acquire()
            if self.blockiert:
                self.blockiert_lock.release()
                time.sleep(0.2)
                continue
            self.blockiert = True
            self.blockiert_lock.release()
            break
        if vektor['winkel'] > 90 and vektor['winkel'] <= 270:
            self.turnleft(int(round(vektor['winkel'])))
        else:
            self.turnright(int(round(vektor['winkel'])))
        while(True):
            self.blockiert_lock.acquire()
            if self.blockiert:
                self.blockiert_lock.release()
                time.sleep(0.2)
                continue
            self.blockiert = True
            self.blockiert_lock.release()
            break
        self.go_forward(vektor['entfernung'])
        while(True):
            self.blockiert_lock.acquire()
            if self.blockiert:
                self.blockiert_lock.release()
                time.sleep(0.2)
                continue
            self.blockiert_lock.release()
            break
        self.status_lock.acquire()
        if self.status == 0:
            self.status_lock.release()
            return True
        elif self.status == 1:
            self.status_lock.release()
            return False
        else: #TODO: potentiell Exception, oder ziel gefunden
            self.status_lock.release()
            dbg_print('brick.go_to_point(): else', 1)
            return False

    def scan_ultrasonic(self):
        self.send_message(message = '5,0')

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
                dbg_print("exploration_simple - state=%d" % state,1)

                if state == 0:
                    self.go_forward(0)
                elif state == 1:
                    self.protokoll.callRemote(command.SendData, handle=self.handle, point_tag=map.POINT_DODGE_CENTER, x_axis=self.position["x"], y_axis=self.position["y"], yaw=self.ausrichtung)
                    self.go_back(1)
                elif state == 2:
                    linksrechts = random.choice([0, 1]) #0=links || 1=rechts
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
        step = 10
        state = 0
        first_mesurement = 0
        second_mesurement = 0 
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
                dbg_print("exploration_circle - state=%d" % state, 1)

                if state == 0:
                    self.scan_ultrasonic()
                    while True:
                        self.payload_lock.acquire()
                        if self.payload > 0:
                            first_mesurement = self.payload
                            dbg_print("first_mesurement: "+str(first_mesurement), 1)
                            self.payload = 0
                            self.payload_lock.release() 
                            break
                        self.payload_lock.release()
                        time.sleep(0.5)
                    
                    if first_mesurement < 1.5*step:
                        first_mesurement = 0
                        state = 2 #+1 am ende = 3 -> drehen
                    self.protokoll.callRemote(command.SendData, handle=self.handle, point_tag=map.POINT_FREE, x_axis=self.position["x"], y_axis=self.position["y"], yaw=self.ausrichtung)
                elif state == 1:
                    self.go_forward(step)
                elif state == 2:
                    self.protokoll.callRemote(command.SendData, handle=self.handle, point_tag=map.POINT_FREE, x_axis=self.position["x"], y_axis=self.position["y"], yaw=self.ausrichtung)
                    if first_mesurement < 255:
                        self.scan_ultrasonic()
                        while True:
                            self.payload_lock.acquire()
                            if self.payload > 0:
                                second_mesurement = self.payload
                                dbg_print("second_mesurement: "+str(second_mesurement), 1)
                                self.payload = 0
                                self.payload_lock.release() 
                                break
                            self.payload_lock.release() 
                            time.sleep(0.5)
                            
                        if second_mesurement < first_mesurement:
                            self.calibrationFactor = float(step)/(first_mesurement - second_mesurement)
                            dbg_print("calibrationFactor: %.2f" % self.calibrationFactor, 1)
                    else:
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                    step += 10
                elif state == 3:
                    first_mesurement = 0
                    second_mesurement = 0
                    self.turnleft(90)
                state += 1
                state %= 4
                step %= 200
            else:
                self.blockiert_lock.release()

    def exploration_radar(self):
        step = 20
        forward = 10
        state = 1
        direction = 1
        first_mesurement = 0
        second_mesurement = 0 
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
                dbg_print("exploration_radar - state=%d" % state, 1)
                if state == 0:
                    if direction < 2:
                        self.turnright(90)
                    else:
                        self.turnleft(90)
                    direction += 1
                    direction %= 4
                elif state == 1:
                    self.scan_ultrasonic()
                    while True:
                        self.payload_lock.acquire()
                        if self.payload > 0:
                            first_mesurement = self.payload
                            dbg_print("first_mesurement: "+str(first_mesurement), 1)
                            self.payload = 0
                            self.payload_lock.release() 
                            break
                        self.payload_lock.release()
                        time.sleep(0.5)
                    
                    if first_mesurement < 1.5*forward:
                        state = -1 #+1 am ende = 0 -> drehen
                        first_mesurement = 0
                elif state == 2:
                    self.go_forward(forward)
                elif state == 3:
                    if first_mesurement < 255:
                        self.scan_ultrasonic()
                        while True:
                            self.payload_lock.acquire()
                            if self.payload > 0:
                                second_mesurement = self.payload
                                dbg_print("sec_mesurement: "+str(second_mesurement), 1)
                                self.payload = 0
                                self.payload_lock.release() 
                                break
    
                            self.payload_lock.release() 
                            time.sleep(0.5)
                        
                        if second_mesurement < first_mesurement:
                            self.calibrationFactor = float(forward)/(first_mesurement - second_mesurement)
                            dbg_print("calibrationFactor: %.2f" % self.calibrationFactor, 1)
                    else:
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                elif state == 4:
                    first_mesurement = 0
                    second_mesurement = 0
                    if direction < 2:
                        self.turnright(90)
                    else:
                        self.turnleft(90)
                    direction += 1
                    direction %= 4
                elif state == 5:
                    self.scan_ultrasonic()
                    while True:
                        self.payload_lock.acquire()
                        if self.payload > 0:
                            first_mesurement = self.payload
                            dbg_print("first_mesurement: "+str(first_mesurement), 1)
                            self.payload = 0
                            self.payload_lock.release() 
                            break
                        self.payload_lock.release() 
                        time.sleep(0.5)
                        
                    if first_mesurement < 1.5*step:
                        state = -1 #+1 am ende = 0 -> drehen
                        first_mesurement = 0
                elif state == 6:
                    self.go_forward(step)
                    step += 20
                elif state == 7:
                    if first_mesurement < 255:
                        self.scan_ultrasonic()
                        while True:
                            self.payload_lock.acquire()
                            if self.payload > 0:
                                second_mesurement = self.payload
                                dbg_print("second_mesurement: "+str(second_mesurement), 1)
                                self.payload = 0
                                self.payload_lock.release() 
                                break
                            self.payload_lock.release() 
                            time.sleep(0.5)
                            
                        if second_mesurement < first_mesurement:
                            self.calibrationFactor = float(step)/(first_mesurement - second_mesurement)
                            dbg_print("calibrationFactor: %.2f" % self.calibrationFactor, 1)
                    else:
                        self.blockiert_lock.acquire()
                        self.blockiert = False
                        self.blockiert_lock.release()
                state += 1
                state %= 8
                step %= 200
            else:
                self.blockiert_lock.release()


    def exploration_cancel(self):
        while(phase == 0):
            intervall = random.choice([30.0, 60.0])
            time.sleep(intervall)
            if phase == 0:
                self.abbruch_lock.acquire()
                self.abbruch = True
                self.abbruch_lock.release()
                self.stop()
                print "exploration_cancel - abbruch= True gewartet fuer %d sek" % intervall

    def find_programs(self):
        ff = FileFinder(self.brick, "*.rxe")
        for f in ff:
            print(f)

    def start_app(self, app):
        self.brick.start_program(app)

    def send_message(self, message = '', ident = 99):
        if ident == 99:
            self.message_id += 1
            self.message_id %= 10
            ident = self.message_id
        tstr = str(ident) + ";" + message
        dbg_print(tstr, 6)
        self.brick.message_write(self.outbox, tstr)

    def recv_message(self):
        t = self.brick.message_read(self.inbox, self.inbox, True)
        dbg_print(t, 6)
        return t

    def dispatch(self):
        dbg_print("run dispatch", 2)
        count = 0
        while(True):
            if count % 100000 == 0:
                dbg_print("dispatch() - #" + str(count), 3)
            try:
                _, message = self.recv_message()
                dbg_print("message: " + str(message), 9)
                try:
                    t_id, payload = str(message).split(';')
                    ident = int(t_id)
                except:
                    dbg_print("message-parsing-error: falsches Format")
                dbg_print("ident=" + str(t_id) + " msg=" + str(payload), 4)
                csv = payload.split(',') #TODO: payload = event, entfernung, sensor(optional)
                if int(csv[0]) == 1: #nach Zeitintervall 500ms update_position (Entfernung)
                    dbg_print("Update: " + str(csv[1]) + " Einheiten gefahren",1)
                    self.position_lock.acquire()
                    print berechnePunkt(self.ausrichtung, csv[1], self.position)#TODO an MCC
                    self.position_lock.release()
                elif int(csv[0]) == 2: #kollision update_position (Entfernung)
                    self.status_lock.acquire()
                    self.status = 1 # hit
                    self.status_lock.release()
                    dbg_print("Kollision: " + str(csv[1]) + " Einheiten gefahren",1)
                    self.position_lock.acquire()
                    self.position = berechnePunkt(self.ausrichtung,int(str(csv[1]).strip("\x00")),self.position)
                    self.position_lock.release()
                    dbg_print(str(self.position),2)
                    self.blockiert_lock.acquire()
                    self.blockiert = False
                    self.blockiert_lock.release()
                elif int(csv[0]) == 3: #strecke ohne vorkommnisse abgefahren
                    self.status_lock.acquire()
                    self.status = 0 #arrived
                    dbg_print("status: arrived(%d)" %self.status, 1)
                    self.status_lock.release()
                    dbg_print(str(csv[1]) + " Einheiten gefahren",1)
                    self.position_lock.acquire()
                    self.position = berechnePunkt(self.ausrichtung,int(str(csv[1]).strip("\x00")),self.position)
                    self.position_lock.release()
                    self.blockiert_lock.acquire()
                    self.blockiert = False
                    self.blockiert_lock.release()
                elif int(csv[0]) == 4: #beendet rueckwaerts und drehen
                    dbg_print("Drehen oder Zurueck",1)
                    self.blockiert_lock.acquire()
                    self.blockiert = False
                    self.blockiert_lock.release()
                elif int(csv[0]) == 5:
                    self.payload_lock.acquire()
                    self.payload = int(str(csv[1]).strip("\x00"))
                    self.payload_lock.release()
                    self.blockiert_lock.acquire()
                    self.blockiert = False
                    self.blockiert_lock.release()
                elif int(csv[0]) == 9: #ziel gefunden gleich kommt 2
                    dbg_print("Ziel gefunden")
                else:
                    dbg_print("csv konnt nicht geparst werden")
            except:
                pass
            count += 1

    def work(self):
        time.sleep(3.0)
        t = threading.Thread(target = self.exploration_cancel, args = ())
        t.setDaemon(True)
        t.start()
        while(phase == 0):
            time.sleep(1.0)
            if self.handle == None:
                continue
            self.abbruch_lock.acquire()
            if self.abbruch:
                self.abbruch = False
                self.abbruch_lock.release()
                if phase == 0:
                    algo = random.choice([2])
                    if algo == 0:
                        self.exploration_simple() #blockierender Aufruf
                    elif algo == 1:
                        self.exploration_radar() #blockierender Aufruf
                    elif algo == 2:
                        self.exploration_circle() #blockierender Aufruf
            else:
                self.abbruch_lock.release()



class NXTClient():

    def __init__(self, anzahl = 1):
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
                self.factory.robots[bot] = Explorer(MAC[bot], self.protocol, bot, bot + 1, 5 + bot, 1 + bot)
            except:
                print "Bot %s nicht gefunden" % MAC[bot]
                self.factory.robots[bot] = None
            if self.factory.robots[bot] != None:
                deffered = protocol.callRemote(command.Register,
                                               robot_type = self.factory.robots[bot].robot_type,
                                               color = self.factory.robots[bot].color, rhandle = bot)
                deffered.addCallback(self.activate)
                deffered.addErrback(self.failure)

    def activate(self, handle):
        self.factory.robots[handle['rhandle']].handle = handle['handle']
        print "handle=%s" % (self.factory.robots[handle['rhandle']].handle)
        deffered = self.protocol.callRemote(command.Activate, handle = self.factory.robots[handle['rhandle']].handle)
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
