from math import sin, cos
import random
from utils import Point

__author__ = 'mhhf'

class Simulator(object):

    def __init__(self):
        self.nxtList = []


    def generateList(self):

        #point = Point(0,0,0)
        pointX = 0
        pointY = 0
        yaw = 0

        direction = 0

        #generate List
        for i in range(100):
            # adding Point to List
            #

            # compute new Point

            # change Direction?
            if random.randint(0,9)==0:
                r = random.randint(0,2)
                if(r==0):
                    direction = -1
                elif(r==1):
                    direction = 1
                else:
                    direction = 0

            # Compute new Position
            dh = random.normalvariate(0,1)*2.25*2
            dr = yaw + random.normalvariate(0,1)*2.25*direction

            dx = sin(dr)*dh
            dy = -cos(dr)*dh

            pointX += dx
            pointY += dy
            yaw = dr
            point = Point(pointX.__int__(), pointY.__int__(), yaw)
            self.nxtList.append(point)

