import sys
import time
import threading
from nxt_debug import dbg_print, DEBUGLEVEL
from threading import Thread
import nxt.direct
from nxt.brick import Brick, FileFinder
from nxt.locator import find_one_brick
from nxt.locator import Method

TIMEOFFSET = 3.0 #zeit bis zum nochmaligen Senden

class pseudoBrick():
    def __init__(self):
        self.liste = [(11, 'r;6;bla')]
    
    def start_program(self, app):
        pass
    
    def message_write(self, outbox, message):
        dbg_print("message write: "+message,2)
        time.sleep(1.0/10)

    def message_read(self, inbox1, inbox2, leeren):
        time.sleep(5)
        return self.liste.pop()

class Explorer():
    def __init__(self, mac, outbox=5, inbox=1):
        if DEBUGLEVEL < 7:
            self.brick = find_one_brick(host=mac, method=Method(usb=False, bluetooth=True))
        else:
            self.brick = pseudoBrick()
        self.message_id = 0
        self.remote_message_id = 0
        self.outbox = outbox
        self.inbox = 10 + inbox
        self.timelist = []
        self.lock = threading.Lock()     
        self.start_app("bt_test.rxe")
        dispatcher = Thread(target=self.dispatch, args=())
        dispatcher.start()
        
    def __del__(self):
        pass
        
    def turnright(self, degrees):
        pass
    
    def turnleft(self,  degrees):    
        pass
        
    def go_forward(self, distance):
        pass
        
    def go_back(self, distance):
        pass
    
    def find_programs(self):
        ff = FileFinder(robo.brick, "*.rxe")
        for f in ff:
            print(f)
    
    def start_app(self, app):
        self.brick.start_program(app)
        
    def send_message(self, message = '', typ = 'm', id = 99):
        if typ == 'm':
            self.message_id += 1
            self.message_id %= 10
            id = self.message_id
        robo.brick.message_write(self.outbox, typ+";"+str(id)+";"+message)
        if typ != 'a':
            dbg_print('timelist.append: '+str((time.time(), typ, id, message)),3)
            self.timelist.append((time.time(), typ, id, message))

    def recv_message(self):
        return robo.brick.message_read(self.inbox, self.inbox, True)

    def timelist_access(self, choose, id):
        self.lock.acquire()
        dbg_print("timelist_access lock",3)
        if choose == 'r' or choose == 'a':
            for tupel in self.timelist:
                if tupel[2] == id:
                    self.timelist.remove(tupel)
        elif choose == 't':         
            for tupel in self.timelist:
                if tupel[0]+TIMEOFFSET <= time.time():
                    self.timelist.remove(tupel)
                    self.send_message(message=tupel[3], typ=tupel[1], id=tupel[2])
        dbg_print("timelist: "+str(self.timelist),3)
        self.lock.release() 
        dbg_print("timelist_access unlock",3)

    def dispatch(self):       
        dbg_print("run dispatch",2)
        dbg_print("run timer",2)
        t = Thread(target=self.timer, args=())
        t.start()
        dbg_print("BT-Empfang",1)
        count = 0
        while(True):
            if count%100 == 0:
                dbg_print("DispatcherSchleife Durchlauf: "+str(count),3)
            try:
                local_box, message = self.recv_message()
                dbg_print((local_box, message),3)
                try: 
                    typ, t_id, payload = str(message).split(';')
                    id = int(t_id)
                except:
                    dbg_print("message-parsing-error: falsches Format")
                    
                if typ == 'm':
                    self.remote_message_id = id
                    # irgendetwas mit payload machen
                    self.send_message(typ='r', id=self.remote_message_id, message='resp')
                    
                elif typ == 'r':
                    self.timelist_access(typ, id)
                    self.send_message(typ='a', id=id, message='ack')

                elif typ == 'a':
                    self.timelist_access(typ, id)
                else:
                    dbg_print('Falscher Nachrichtentyp')
            except:
                pass
            count += 1
            
    def timer(self):
        while(True):
            time.sleep(3.0)
            self.timelist_access('t', 0)    
    

if __name__ == '__main__':
    dbg_print('suche robo',1)
    robo = Explorer(mac="00:16:53:10:48:F3")
    if robo != None: 
        dbg_print("robo gefunden",1)
    else: 
        dbg_print("no robo",1)
        sys.exit()
    for i in range(4):
        robo.send_message(message='Hans'+str(i))
    print("fertig")
