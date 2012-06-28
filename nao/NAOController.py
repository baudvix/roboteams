__author__ = 'Lorenz'

import NAOCalibration
from optparse import OptionParser

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

    def len(self):
        return len(self.arr)

def main():
    q = queue()
    # enqueue some NXTNumbers
    q.enqueue([0,"blue"])
    q.enqueue([2,"green"])
    q.enqueue([1,"red"])

    for i in range(0, q.len()):
        element = q.dequeue()
        NAOCalibration.performCalibration(element[0], element[1])

main()