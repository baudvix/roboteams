# Get an image from NAO. Display it and save it using PIL.

import time
import cv
import math

# Python Image Library
import Image
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

def getColour(IP, PORT, x, y):
    """
    First get an image from Nao, then show it on the screen with PIL.
    """
    print "-----start:getColour-----"

    time1 = time.clock()

    try:
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
        areas = [0,0,0,0]
        colors = ['red', 'green', 'blue', 'black']

        videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

        # Get a camera image.
        # image[6] contains the image data passed as an array of ASCII chars.
        naoImage = camProxy.getImageRemote(videoClient)

        camProxy.unsubscribe(videoClient)

        # Now we work with the image returned and save it as a JPG  using ImageDraw
        # package.

        # Get the image size and pixel array.
        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]

        # Create a PIL Image from our pixel array.
        im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

        # Save the image.
        im.save("camImage.jpg", "JPEG")

        #im.show()

        color = 'red'
        img = cv.LoadImage('camImage.jpg')
        #  img = cv.QueryFrame( self.capture )

        #blur the source image to reduce color noise
        cv.Smooth(img, img, cv.CV_BLUR, 3);

        #convert the image to hsv(Hue, Saturation, Value) so its
        #easier to determine the color to track(hue)
        hsv_img = cv.CreateImage(cv.GetSize(img), 8, 3)
        cv.CvtColor(img, hsv_img, cv.CV_BGR2HSV)
        t1 = time.clock()

        #limit all pixels that don't match our criteria, in this case we are
        #looking for purple but if you want you can adjust the first value in
        #both turples which is the hue range(120,140).  OpenCV uses 0-180 as
        #a hue range for the HSV color model
        t3 = time.clock()
        thresholded_img =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
        for u in range(0, 1):
            for h in range(0, len(colors)):
                if (colors[h] == 'red' ):
                    #cv.InRangeS(hsv_img, (140, 80, 80), (180, 180, 180), thresholded_img)
                    cv.InRangeS(hsv_img, (0, 100, 100), (40, 255, 255), thresholded_img)
                if (colors[h] == 'green' ):
                    cv.InRangeS(hsv_img, (50, 40, 40), (90, 180, 255), thresholded_img)
                if (colors[h] == 'blue' ):
                    cv.InRangeS(hsv_img, (100, 100, 110), (140, 255, 255), thresholded_img)
                #if (colors[h] == 'black' ):
                #    cv.InRangeS(hsv_img, (0, 0, 0), (180, 10, 100), thresholded_img)
                #determine the objects moments and check that the area is large
                #enough to be our object
                moments = cv.Moments(cv.GetMat(thresholded_img,1), 0)
                area = cv.GetCentralMoment(moments, 0, 0)
                #there can be noise in the video so ignore objects with small areas


                if(area > 1):
                    #determine the x and y coordinates of the center of the object
                        #we are tracking by dividing the 1, 0 and 0, 1 moments by the area
                    x_new = cv.GetSpatialMoment(moments, 1, 0)/area
                    y_new = cv.GetSpatialMoment(moments, 0, 1)/area
                    print colors[h] + ' x: ' + str(x_new) + ' y: ' + str(y_new) + ' area: ' + str(area)

                    #if ( (abs(x_new - xValue) < 100) & (abs(y_new - yValue) < 100)):
                    print 'Abstand x: ', (abs(x_new - xValue)), ' y: ', (abs(y_new - yValue))
                    areas[h] = int(math.sqrt((abs(x_new - xValue)*abs(x_new - xValue)) + (abs(y_new - yValue)*abs(y_new - yValue))))
                    #tts = ALProxy("ALTextToSpeech")
                        #tts.say( colors[h] + 'Marker found')
                        #y = 100
                        #x = 100
                        #if((abs(y-y_new) <= 100) & (abs(x-x_new) <= 100)):
                        #    print 'found'
                        #    return 'true'
                        #else:
                        #    return 'false'
                else:
                    areas[h] = 99999
                    print colors[h] + 'area' + str(area)

            biggest = 0

            for u in range(0, len(colors)-1):
                if (areas[biggest] > areas[u+1]):
                    biggest = u+1

            time2 = time.clock()

            print("WAHRSCHEINLICHSTE FARBE: " + colors[biggest])
            print "Whole time needed: "+str(time2-time1)
            print "-----end:getColour-----"
            return biggest

    except Exception:
        print Exception
        return -1

if __name__ == '__main__':
    IP = "localhost"
    PORT = 9559

    naoImage = getColour(IP, PORT, 320, 240)