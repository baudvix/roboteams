# Get an image from NAO. Display it and save it using PIL.

import sys
import time
import cv
import math

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
    #path = "/home/guenthse/uni/semesterprojekt/nao_images/"
    path = "/Users/Lorenz/images/"

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

    t0 = time.time()

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
    im.save(path+ "/camImage" + str(t0) + ".jpg", "JPEG")

    #im.show()

    color = 'red'
    img = cv.LoadImage(path+"camImage" + str(t0) + ".jpg")
    #  img = cv.QueryFrame( self.capture )

    #blur the source image to reduce color noise
    cv.Smooth(img, img, cv.CV_BLUR, 3);

    #convert the image to hsv(Hue, Saturation, Value) so its
    #easier to determine the color to track(hue)
    hsv_img = cv.CreateImage(cv.GetSize(img), 8, 3)
    cv.CvtColor(img, hsv_img, cv.CV_BGR2HSV)

    #limit all pixels that don't match our criteria, in this case we are
    #looking for purple but if you want you can adjust the first value in
    #both turples which is the hue range(120,140).  OpenCV uses 0-180 as
    #a hue range for the HSV color model
    thresholded_img =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
    for u in range(0, 1):
        for h in range(0, len(colors)):
            if (colors[h] == 'red' ):
                cv.InRangeS(hsv_img, (0, 70, 80), (15, 255, 255), thresholded_img)
                cv.Merge(thresholded_img, None, None, None, img)
                cv.ShowImage("gray",img)
                cv.ShowImage("dst",thresholded_img)
                cv.SaveImage(path+"/red2"+str(t0)+".jpg",img)

            if (colors[h] == 'green' ):
                #cv.InRangeS(hsv_img, (40, 70, 75), (94, 255, 255), thresholded_img)
                cv.InRangeS(hsv_img, (30, 50, 50), (94, 255, 255), thresholded_img)
                cv.Merge(thresholded_img, None, None, None, img)
                cv.ShowImage("gray",img)
                cv.ShowImage("dst",thresholded_img)
                cv.SaveImage(path+"/green"+str(t0)+".jpg",img)

            if (colors[h] == 'blue' ):
                cv.InRangeS(hsv_img,  (95, 95, 85), (135, 255, 255), thresholded_img)
                cv.Merge(thresholded_img, None, None, None, img)
                cv.ShowImage("gray",img)
                cv.ShowImage("dst",thresholded_img)
                cv.SaveImage(path+"/blue"+str(t0)+".jpg",img)

            #while cv.WaitKey(0)!=10:
            #    pass
            print cv.WaitKey(0)

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

        for u in range(0, len(colors)):
            if (areas[biggest] > areas[u]):
                biggest = u

        print("WAHRSCHEINLICHSTE FARBE: " + colors[biggest])
        return biggest
                #create an overlay to mark the center of the tracked object
            #overlay = cv.CreateImage(cv.GetSize(img), 8, 3)

            #cv.Circle(img, (int(x), int(y)), 1, (255, 255, 255), 10)
            #cv.Add(img, overlay, img)
            #add the thresholded image back to the img so we can see what was
            #left after it was applied
            #cv.Merge(thresholded_img, None, None, None, img)

            #display the image
        #cv.ShowImage(color_tracker_window, img)

if __name__ == '__main__':
    IP = "194.95.174.165"
    PORT = 9559
    naoImage = getColour(IP, PORT, 320, 240)