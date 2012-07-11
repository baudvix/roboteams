import time
import random
from nxt_debug import dbg_print

def find_one_brick(host, method):
    return pseudoBrick()

class pseudoBrick():
    def __init__(self):
        self.liste = []
        self.ident = 10
    
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
        if random.choice([0,1])==0:
            msg = self.liste.pop(0)
        else:
            msg = "m;"+str(self.ident)+";h,300"
            self.ident+=1
            self.ident%=10
            self.ident+=10
        dbg_print("pseudoBrick.message_read() - "+str(msg),7)
        time.sleep(1)
        return (11, msg)