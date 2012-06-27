from math import cos, sin
import random
import math
from mcc.utils import Point
from mcc.control.example import nxtclient
from mcc.control import command


class Simulator(object):

    def __init__(self):
        self.nxt_list = []
        self.point_x = 50
        self.point_y = 50
        self.dx = 0
        self.dy = 0
        self.yaw = 0

    def generate_list(self):

        #point = Point(0,0,0)
        self.point_x = 0
        self.point_y = 0
        self.yaw = 0

        self.direction = 0

        #generate List
        for _ in range(200):
            # adding Point to List

            # compute new Point
            point = self.go_point()
            self.nxt_list.append(point)

    def go_point(self):

        """

        """
        while True:
            # change Direction?
            if not random.randint(0, 9):
                self.direction = 0
            else:
                self.direction = 1

            # Compute new Position
            dh = random.normalvariate(0, 1) * 2.25 * 4
            dr = random.normalvariate(0, 1) * 2.25 * math.pi

            if self.direction == 1 and self.dx != 0 and self.dy != 0:
                pass
            else:
                self.dx = sin(dr) * dh
                self.dy = -cos(dr) * dh

            self.point_x += self.dx
            self.point_y += self.dy
            if not (self.point_x < 0 or self.point_y < 0 or self.point_x > 190 or self.point_y > 190):
                self.yaw = dr
                break
            else:
                self.point_x -= self.dx
                self.point_y -= self.dy

        point = Point(self.point_x.__int__(), self.point_y.__int__(), self.yaw)
        return point


class SimulatorNXT(nxtclient.NXTClient):

    def __init__(self):
        nxtclient.NXTClient.__init__(self, 1)
        self._sim = Simulator()

    def run(self):
        p = self._sim.go_point()
        point_tag = random.randint(0, 4)
        deffered = self.protocol.callRemote(command.SendData, handle=self.handle, point_tag=point_tag,
            x_axis=p.x_coord, y_axis=p.y_coord, yaw=p.yaw)
        deffered.addCallback(self.success)
        deffered.addErrback(self.failure)
