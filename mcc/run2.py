#!/usr/bin/env python2
import sys
sys.path.append("..")
from mcc.control import server2


def main():
    server2.MCCServer()


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
