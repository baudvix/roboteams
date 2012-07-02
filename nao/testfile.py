__author__ = 'Lorenz'

import config
from config import IP
from config import PORT
import time
import motion_poseInit
import math
from naoqi import ALProxy

import Queue

class queue():
    def __init__(self):
        self.arr = []

    def enqueue(self, element):
        self.arr.append(element)

    def dequeue(self):
        if(len(self.arr)>0):
            element = self.arr[0]
            self.arr = self.arr[1:len(self.arr)]
            return element
        return -1

    def first(self):
        if(len(self.arr)>0):
            return self.arr[0]
        return -1

    def last(self):
        if(len(self.arr)>0):
            return self.arr[len(self.arr)-1]
        return -1

def main():
    q = queue()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    print q.dequeue()
    print q.dequeue()
    print q.dequeue()
    print q.dequeue()
    print q.first()

    p = Queue()
    print p

main()






