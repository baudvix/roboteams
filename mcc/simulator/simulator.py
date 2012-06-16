from math import sin, cos
import random
import math
from utils import Point

__author__ = 'mhhf'

class Simulator(object):

    def __init__(self):
        self.nxtList = []


    def generateList(self):

        #point = Point(0,0,0)
        self.pointX = 50
        self.pointY = 50
        self.yaw = 0

        self.direction = 0

        #generate List
        for i in range(100):
            # adding Point to List
            #

            # compute new Point
            point = self.goPoint()
            self.nxtList.append(point)

    def goPoint(self):

        # change Direction?
        if random.randint(0,9)==0:
            r = random.randint(0,2)
            if(r==0):
                self.direction = -1
            elif(r==1):
                self.direction = 1
            else:
                self.direction = 0

        # Compute new Position
        dh = random.normalvariate(0,1)*2.25*4
        dr = random.normalvariate(0,1)*2.25*math.pi

        dx = sin(dr)*dh
        dy = -cos(dr)*dh

        self.pointX += dx
        self.pointY += dy
        self.yaw = dr
        point = Point(self.pointX.__int__(), self.pointY.__int__(), self.yaw)
        return point
