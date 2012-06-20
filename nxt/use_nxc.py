import sys
import time
import threading
from nxt_debug import dbg_print, DEBUGLEVEL
from threading import Thread
import nxt.direct
from nxt.brick import Brick, FileFinder
from nxt.locator import find_one_brick
from nxt.locator import Method

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
        self.brick = pseudoBrick()#find_one_brick(host=mac, method=Method(usb=False, bluetooth=True))
        self.message_id = 0
        self.remote_message_id = 0
        self.outbox = outbox
        self.inbox = 10 + inbox
        self.timelist = []
        self.lock = threading.Lock()
        self.com_state = 0 #FIXME:0 fuer test =1
        #com_state:
        #    0: warte - nichts gesendet, nichts empfangen
        #    1: m gesendet, r noch nicht empfangen
        #    2: m empfangen, r gesendet, warte auf a
        
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
        
    def send_message(self, message):
        robo.brick.message_write(self.outbox, message)
        typ, t_id, payload = str(message).split(';')
        id = int(t_id)
        if typ == 'm':
            self.com_state = 1
        elif typ == 'r':
            self.com_state = 2
        elif typ == 'a':
            self.com_state = 0
        dbg_print('timelist.append: '+str((time.time(), typ, id, payload)),3)
        self.timelist.append((time.time(), typ, id, payload))

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
                if tupel[0] <= time.time():
                    self.timelist.remove(tupel)
                    self.send_message(tupel[1]+';'+str(tupel[2])+';'+tupel[3])
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
                    dbg_print("dispatcher timelist: "+str(self.timelist),3)
                    typ, t_id, payload = str(message).split(';')
                    id = int(t_id)
                except:
                    dbg_print("message-parsing-error: falsches Format")
                    
                if self.com_state == 0: #warten auf m
                    if typ == 'm':
                        self.remote_message_id = id
                        # irgendetwas mit payload machen
                        self.send_message('r;'+str(self.remote_message_id)+';;')
                    else:
                        dbg_print("com_state - Fehler im Zustandsautomaten")
                elif self.com_state == 1: #m gesendet, warte r, sende a
                    if typ == 'r' and id == self.message_id:
                        self.timelist_access(typ, id)
                        self.send_message('a;'+str(self.message_id)+';;')
                        self.message_id += 1
                        self.message_id %= 10
                    else:
                        dbg_print("com_state - Fehler im Zustandsautomaten")
                elif self.com_state == 2: #m empfangen, r gesendet, warte auf a
                    if typ == 'a' and id == self.remote_message_id:
                        self.timelist_access(typ, id)
                        self.com_state = 0
                    else:
                        dbg_print("com_state - Fehler im Zustandsautomaten")
                else:
                    dbg_print("com_state - Fehler im Zustandsautomaten")
            except:
                pass
            count += 1
            
    def timer(self):
        while(True):
            time.sleep(3)
            self.timelist_access('t', 0)    
    

if __name__ == '__main__':
    dbg_print('suche robo',1)
    robo = Explorer(mac="00:16:53:10:48:F3")
    if robo != None: 
        dbg_print("robo gefunden",1)
    else: 
        dbg_print("no robo",1)
        sys.exit()
    robo.start_app("bt_test.rxe")
    dispatcher1 = Thread(target=robo.dispatch, args=())
    dispatcher1.start()
        
    robo.message_id = 6
    robo.send_message('m;'+str(robo.message_id)+';HansWurst')
    dispatcher1.join()
    print("fertig")
