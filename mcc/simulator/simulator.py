from math import cos, sin
import random
import math
from mcc.utils import Point

class Simulator(object):

    def __init__(self):
        self.nxt_list = []
        self.point_x = 50
        self.point_y = 50
        self.yaw = 0


    def generate_list(self):

        #point = Point(0,0,0)
        self.point_x = 50
        self.point_y = 50
        self.yaw = 0

        self.direction = 0

        #generate List
        for _ in range(100):
            # adding Point to List

            # compute new Point
            point = self.go_point()
            self.nxt_list.append(point)

    def go_point(self):

        while True:
            #TODO use direction
            # change Direction?
            if not random.randint(0, 9):
                r = random.randint(0, 2)
                if not r:
                    self.direction = -1
                elif r == 1:
                    self.direction = 1
                else:
                    self.direction = 0

            # Compute new Position

            dh = random.normalvariate(0, 1)*2.25*4
            dr = random.normalvariate(0, 1)*2.25*math.pi

            dx = sin(dr)*dh
            dy = -cos(dr)*dh

            print "dh: ", dh, "\ndr: ", dr, "\ndx: ", dx, "\ndy: ", dy

            self.point_x += dx
            self.point_y += dy
            self.yaw = dr
            if not (self.point_x < 0 or self.point_y < 0):
                break

        point = Point(self.point_x.__int__(), self.point_y.__int__(), self.yaw)
        return point
