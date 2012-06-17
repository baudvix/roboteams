from threading import _start_new_thread, Thread
#LEGO
from nxt.brick import Brick
from nxt.locator import find_one_brick
from nxt.motor import Motor, PORT_A, PORT_B, PORT_C
from nxt.sensor import *
from nxt.sensor.hitechnic import Compass
from dummy_thread import start_new_thread

TURN_POWER = 80
ACCURACY = 3 
SAMPLE = 4
RADAR_MOTOR_POWER = 100
RADAR_VOLLWINKEL = 7000
TURN_ADJUSTMENT = 7.5

class Turn(Thread):
    def __init__(self, motor, grad, richtung):
        self.motor = motor
        self.richtung = richtung
        self.grad = grad
    
    def run(self):
        self.motor.weak_turn(self.richtung*TURN_POWER, TURN_ADJUSTMENT*self.grad)

class Radar():
    def __init__(self, brick,  port_motor,  port_uc):
        self.radar_motor = Motor(brick, port_motor)
        self.radar_sensor = Ultrasonic(brick, port_uc)
        self.set_startposition()

    def set_startposition(self):
        self.radar_motor.turn(-1*RADAR_MOTOR_POWER, RADAR_VOLLWINKEL/2) 
    
    def perform_scan(self):
        def measure(self):
            total = 0
            for j  in range(ACCURACY):
                part = self.radar_sensor.get_sample()
                total += part
            return total/ACCURACY
         
        result = [] 
        for i in range(SAMPLE):  
            result.append(measure(self))
            self.radar_motor.turn(RADAR_MOTOR_POWER, RADAR_VOLLWINKEL/SAMPLE)

        result.append(measure(self))
         
        self.radar_motor.turn(-1*RADAR_MOTOR_POWER, RADAR_VOLLWINKEL)
        return result
  
class Explorer():
    def __init__(self, mac):
        self.brick = find_one_brick(host=mac)
        self.left = Motor(self.brick, PORT_B)
        self.right = Motor(self.brick, PORT_C)
        #self.compass = Compass(self.brick, PORT_2)
        #self.radar = Radar(self.brick, PORT_A, PORT_1)
        #TODO: Farbsensor
        
    def __del__(self):
        #self.radar.radar_motor.turn(RADAR_MOTOR_POWER, RADAR_VOLLWINKEL/2)
        pass
        
    def turnright(self, degrees):
        start_new_thread(self.left.weak_turn, (-1*TURN_POWER, TURN_ADJUSTMENT*degrees))
        start_new_thread(self.right.weak_turn, (TURN_POWER, TURN_ADJUSTMENT*degrees))
    
    def turnleft(self,  degrees):
        #self.right.weak_turn(-1*TURN_POWER, TURN_ADJUSTMENT*degrees)
        #self.left.weak_turn(TURN_POWER, TURN_ADJUSTMENT*degrees)
        
        t1 = Turn(self.right, degrees, -1)
        t2 = Turn(self.left, degrees, 1)
        
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

    def scan(self):
        for value in self.radar.perform_scan():
            print 'sample: ', 'Entferung: ',  value, 'cm'
    
    def bearing(self):
        total = 0
        for i in range(ACCURACY):
            total += self.compass.get_sample()
        print 'Grad von Nord:', total/ACCURACY

