import random
import math
import sys
sys.path.append("../..")
from mcc.utils import Point
from mcc.example import nxtclient
from mcc.control import command
from mcc.simulator import fake
from mcc.model import map


class Simulator(object):

    def __init__(self):
        self.nxt_list = []
        self.point_x = 50
        self.point_y = 50
        self.yaw = random.random() * math.pi * 2
        self.speed = 5
        self.fake_map = fake.FakeMap(5, size=350)
        self.logfile = open('./base2.txt')

    def go_point(self, n):

        # tmp_x = int(self.point_x + self.speed * math.cos(self.yaw))
        # tmp_y = int(self.point_y + self.speed * math.sin(self.yaw))
        vals = self.logfile.readline().replace('\n', '').split(',')

        tmp_x = int(vals[2])
        tmp_y = int(vals[3])

        # if hit rotate from 45 to 135 degrees
        # if self.fake_map.hit(tmp_x, tmp_y, self.yaw):
        #     rotate = random.random() * 90 + 45
        #     self.yaw = self.yaw + math.radians(rotate)
        #     self.yaw = self.yaw % math.pi * 2
        #     return self.go_point(n - 1)
        self.point_x = tmp_x
        self.point_y = tmp_y
        point = Point(self.point_x, self.point_y, self.yaw)
        return point


class SimulatorNXT(nxtclient.NXTClient):

    def __init__(self):
        self._sim = Simulator()
        nxtclient.NXTClient.__init__(self, 1)

    def run(self):
        if self.active:
            p = self._sim.go_point(8)
            point_tag = map.POINT_FREE
            if self._sim.fake_map.hit_target(p.x_coord, p.y_coord):
                point_tag = map.POINT_TARGET
            deffered = self.protocol.callRemote(command.SendData, handle=self.handle, point_tag=point_tag,
                x_axis=p.x_coord, y_axis=p.y_coord, yaw=p.yaw)
            deffered.addCallback(self.success)
            deffered.addErrback(self.failure)

if __name__ == '__main__':
    SimulatorNXT()
