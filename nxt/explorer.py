import sys
import time
import threading
from nxt_debug import dbg_print, DEBUGLEVEL
from threading import Thread
from nxt.brick import FileFinder
from nxt.locator import find_one_brick
from nxt.locator import Method

TIMEOFFSET = 3.0 #zeit bis zum nochmaligen Senden
MAC1 = "00:16:53:10:49:4D" 
MAC2 = "00:16:53:10:48:E7"
MAC3 = "00:16:53:10:48:F3"

class pseudoBrick():
    def __init__(self):
        self.liste = []
    
    def start_program(self, app):
        pass
    
    def message_write(self, outbox, message):
        dbg_print("pseudoBrick.message_write(): "+message,7)
        time.sleep(0.1)
        typ, ident, _ = message.split(';')
        if typ == 'm':
            self.liste.append('r;'+str(ident)+';resp')
        elif typ == 'r':
            self.liste.append('a;'+str(ident)+';ack')
        elif typ == 'a':
            pass
        else:
            dbg_print("pseudoBrick.message_write() - parse-error")

    def message_read(self, inbox1, inbox2, leeren):
        msg = self.liste.pop()
        dbg_print("pseudoBrick.message_read() - "+str(msg),7)
        time.sleep(2)
        return (11, msg)

class Explorer():
    def __init__(self, mac, outbox=5, inbox=1):
        self.brick = find_one_brick(host=mac, method=Method(usb=True, bluetooth=True))
        #self.brick = pseudoBrick()
        self.message_id = 0
        self.outbox = outbox
        self.inbox = 10 + inbox
        self.timelist = []
        self.lock = threading.Lock()     
        self.start_app("explorer.rxe")
        dispatcher = Thread(target=self.dispatch, args=())
        dispatcher.setDaemon(True)
        dispatcher.start()
        
    def __del__(self):
        pass
    
    def event(self, message):
        pass
    
    def turnright(self, degrees):
        self.send_message(message='4,'+str(degrees))
    
    def turnleft(self,  degrees):    
        self.send_message(message='3,'+str(degrees))
        
    def go_forward(self, distance):
        self.send_message(message='1,'+str(distance))
        
    def go_back(self, distance):
        self.send_message(message='2,'+str(distance))
    
    def find_programs(self):
        ff = FileFinder(robo.brick, "*.rxe")
        for f in ff:
            print(f)
    
    def start_app(self, app):
        self.brick.start_program(app)
        
    def send_message(self, message = '', typ = 'm', ident = 99):
        if typ == 'm' and ident == 99:
            self.message_id += 1
            self.message_id %= 10
            ident = self.message_id
        robo.brick.message_write(self.outbox, typ+";"+str(ident)+";"+message)
        if typ != 'a':
            dbg_print('timelist.append: '+str((time.time(), typ, ident, message)),3)
            self.timelist.append((time.time(), typ, ident, message))

    def recv_message(self):
        t = robo.brick.message_read(self.inbox, self.inbox, True)
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
        t = Thread(target=self.timer, args=())
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
                    event, value = payload.split(',')
                    if event == 's':
                        print "%d Einheiten gefahren" % value
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
    

if __name__ == '__main__' and DEBUGLEVEL > 0:
    dbg_print('suche robo',1)
    robo = Explorer(mac=MAC1)
    if robo != None: 
        dbg_print("robo gefunden",1)
    else: 
        dbg_print("no robo",1)
        sys.exit()
    time.sleep(2.0);    
    #max_int = 32768
    
    dbg_print("__main__ fertig",7)
