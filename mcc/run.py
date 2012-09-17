#!/usr/bin/env python2
import sys
sys.path.append("..")
from mcc.control import headless_server


def main():
    headless_server.MCCServer()


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
