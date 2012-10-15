#!/usr/bin/env python

import random
import math


class FakeMap():

    #target is an circle
    #size is 350 x 350 cm
    #boundary by array limit
    #obstacle by blocked

    def __init__(self, obstacle_possibility, target=(120, 80), size=350):
        self.size = size
        self.target = target
        self.fake_map = [[0 for x in xrange(size)] for y in xrange(size)]
        for x in range(0, size):
            for y in range(0, size):
                if random.randint(0, 100) < obstacle_possibility:
                    self.fake_map[x][y] = 1
                    if self.on_map(x - 1, y):
                        self.fake_map[x - 1][y] = 1
                    if self.on_map(x - 1, y + 1):
                        self.fake_map[x - 1][y + 1] = 1
                    if self.on_map(x, y + 1):
                        self.fake_map[x][y + 1] = 1
                    if self.on_map(x + 1, y + 1):
                        self.fake_map[x + 1][y + 1] = 1
                    if self.on_map(x + 1, y):
                        self.fake_map[x + 1][y] = 1
                    if self.on_map(x + 1, y - 1):
                        self.fake_map[x + 1][y - 1] = 1
                    if self.on_map(x, y - 1):
                        self.fake_map[x][y - 1] = 1
                    if self.on_map(x - 1, y - 1):
                        self.fake_map[x - 1][y - 1] = 1

    def on_map(self, x, y):
        if x <= 0 or x >= self.size:
            return False
        if y <= 0 or y >= self.size:
            return False
        return True

    def hit(self, x, y, yaw):
        if x - 15 < 0 or x + 15 > self.size:
            return True
        if y - 15 < 0 or y + 15 > self.size:
            return True
        #TODO: check if nxt has a dodge on fake map (array[x][y] = 1)
        if random.randint(0, 100) < 5:
            return True
        return False

    def hit_target(self, x, y):
        if self.target[0] > x:
            tmp_x1 = self.target[0]
            tmp_x2 = x
        else:
            tmp_x1 = x
            tmp_x2 = self.target[0]
        if self.target[1] > y:
            tmp_y1 = self.target[0]
            tmp_y2 = y
        else:
            tmp_y1 = y
            tmp_y2 = self.target[0]
        x = tmp_x1 - tmp_x2
        y = tmp_y1 - tmp_y2
        if math.sqrt(x * x + y * y) < 20:
            return True
        return False
