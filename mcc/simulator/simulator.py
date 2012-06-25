from math import *
import random
import math
from mcc.utils import Point

class Simulator(object):

    def __init__(self):
        self.nxtList = []
        self.pointX = 50
        self.pointY = 50
        self.yaw = 0


    def generateList(self):

        #point = Point(0,0,0)
        self.pointX = 50
        self.pointY = 50
        self.yaw = 0

        self.direction = 0

        #generate List
        for i in range(100):
            # adding Point to List

            # compute new Point
            point = self.goPoint()
            self.nxtList.append(point)

    def goPoint(self):

        while True:
            #TODO use direction
            # change Direction?
            if not random.randint(0, 9):
                r = random.randint(0,2)
                if not r:
                    self.direction = -1
                elif r == 1:
                    self.direction = 1
                else:
                    self.direction = 0

            # Compute new Position

            dh = random.normalvariate(0,1)*2.25*4
            dr = random.normalvariate(0,1)*2.25*math.pi

            dx = sin(dr)*dh
            dy = -cos(dr)*dh

            print "dh: ", dh, "\ndr: ", dr, "\ndx: ", dx, "\ndy: ", dy

            self.pointX += dx
            self.pointY += dy
            self.yaw = dr
            if not (self.pointX < 0 or self.pointY < 0):
                break

        point = Point(self.pointX.__int__(), self.pointY.__int__(), self.yaw)
        return point