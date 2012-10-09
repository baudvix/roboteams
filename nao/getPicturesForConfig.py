# Get an image from NAO. Display it and save it using PIL.

import sys
import time
import cv
import math
import datetime

# Python Image Library
import Image

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule


def getColour(IP, PORT, x, y):
    """
    First get an image from Nao, then show it on the screen with PIL.
    """
    #path = "/home/nao/images/"
    path = "/home/guenthse/uni/semesterprojekt/nao_images/"

    myBroker = ALBroker("myBroker",
        "0.0.0.0",   # listen to anyone
        0,           # find a free port and use it
        IP,         # parent broker IP
        PORT)       # parent broker port

    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    resolution = 2    # VGA
    colorSpace = 11   # RGB

    xValue = x
    yValue = y

    #for b in range(0, 5):
    areas = [0,0,0]
    colors = ['red', 'green', 'blue']

    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

    t0 = datetime.datetime.isoformat(datetime.datetime.now())

    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)

    t1 = time.time()

    # Time the image transfer.
    #print "Runde: ", b

    camProxy.unsubscribe(videoClient)


    # Now we work with the image returned and save it as a PNG  using ImageDraw
    # package.

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    # Create a PIL Image from our pixel array.
    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

    # Save the image.
    im.save(path+ "configColour" + str(t0) + ".jpg", "JPEG")

    #im.show()


if __name__ == '__main__':
    IP = "194.95.174.169"
    PORT = 9559
    naoImage = getColour(IP, PORT, 320, 240)