import sys
import time
from nxt_debug import dbg_print, DEBUGLEVEL
from threading import Thread
#LEGO
import nxt.direct
from nxt.brick import Brick, FileFinder
from nxt.locator import find_one_brick
from nxt.locator import Method

class Explorer():
    def __init__(self, mac, outbox=5, inbox=11):
        self.brick = find_one_brick(host=mac, method=Method(usb=False, bluetooth=True))
        self.message_id = 0
        self.remote_message_id = 0
        self.outbox = outbox
        self.inbox = inbox
        self.com_state = 0 
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

    def recv_message(self):
        return robo.brick.message_read(self.inbox, self.inbox, True)

    def dispatch(self):
        dbg_print("run dispatch",2)
        dbg_print("BT-Empfang",1)
        count = 0
        while(True):
            if count%100 == 0:
                dbg_print("DispatcherSchleife Durchlauf: "+str(count),3)
            try:
                local_box, message = self.recv_message()
                dbg_print((local_box, message),3)
                try: 
                    typ, id, payload = str(message).split(';')
                except:
                    dbg_print("message-parsing-error: falsches Format")
                    
                if self.com_state == 0: #warten auf m
                    if typ == 'm':
                        self.remote_message_id = id
                        # irgendetwas mit payload machen
                        self.send_message('r;'+str(self.remote_message_id)+';;')
                elif self.com_state == 1: #m gesendet, warte r
                    pass
                elif self.com_state == 2: #m empfangen, r gesendet, warte auf a
                    pass
                else:
                    dbg_print("com_state - Fehler im Zustandsautomaten")
            except:
                pass
            count += 1

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
    dispatcher1.join()    
    robo.message_id = 66
    robo.send_message('m;'+str(robo.message_id)+';HansWurst')
    
    print("fertig")
