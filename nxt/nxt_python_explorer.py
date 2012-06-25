from threading import Thread
#LEGO
from nxt.brick import Brick
from nxt.locator import find_one_brick
from nxt.motor import Motor, PORT_A, PORT_B, PORT_C
from nxt.sensor import *
from nxt.sensor.hitechnic import Compass
from dummy_thread import start_new_thread

TURN_POWER = 40
TURN_ADJUSTMENT = 2.08

class Explorer():
    def __init__(self, mac):
        self.brick = find_one_brick(host=mac)
        self.left = Motor(self.brick, PORT_B)
        self.right = Motor(self.brick, PORT_C)
        
    def __del__(self):
        pass
        
    def turnright(self, degrees):
        t1 = Thread(target=self.left.turn, args=(-1*TURN_POWER, TURN_ADJUSTMENT*degrees))
        t2 = Thread(target=self.right.turn, args=(TURN_POWER, TURN_ADJUSTMENT*degrees))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    
    def turnleft(self,  degrees):    
        t1 = Thread(target=self.left.turn, args=(TURN_POWER, TURN_ADJUSTMENT*degrees))
        t2 = Thread(target=self.right.turn, args=(-1*TURN_POWER, TURN_ADJUSTMENT*degrees))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
    def go_forward(self, distance):
        self.left.weak_turn(-100, distance)
        self.right.weak_turn(-100, distance)
        
    def go_back(self, distance):
        self.left.weak_turn(100, distance)
        self.right.weak_turn(100, distance)
