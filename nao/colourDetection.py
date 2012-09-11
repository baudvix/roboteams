import time
import cv
import math
import Image
import datetime

from naoqi import ALProxy
from naoqi import ALBroker

def getColour(IP, PORT, markerSize):
    path = "/home/nao/images/"

    # myBroker = ALBroker(listen to anyone, find a free port and use it, parent broker IP, parent broker port)
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)

    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    resolution = 2    # VGA
    colorSpace = 11   # RGB

    #for b in range(0, 5):
    areas = [0,0,0]
    colors = ['red', 'green', 'blue']

    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

    

    # Get a camera image.
    naoImage = camProxy.getImageRemote(videoClient)

    t0 = datetime.datetime.isoformat(datetime.datetime.now())

    camProxy.unsubscribe(videoClient)

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    xValue = imageWidth/2
    yValue = imageHeight/2

    print "marker size: ", markerSize

    # Create a PIL Image from our pixel array.
    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    # Save the image.
    im.save(path+ "camImage" + str(t0) + ".jpg", "JPEG")

    img = cv.LoadImage(path+"camImage" + str(t0) + ".jpg")

    centerX = imageWidth/2
    centerY = imageHeight/2

    ratio = markerSize/0.6
    topLeftCropCorner = [centerX-math.ceil(ratio * imageWidth * 0.5), centerY-math.ceil(ratio * imageWidth * 0.5)]
    bottomRightCropCorner = topLeftCropCorner + [math.ceil(ratio*imageWidth), math.ceil(ratio*imageWidth)]

    # crop the image if possible
    if(not(topLeftCropCorner < [0,0] or bottomRightCropCorner > [imageWidth,imageHeight])):
        cv.SetImageROI(img, (topLeftCropCorner[0], topLeftCropCorner[1], math.ceil(ratio*imageWidth), math.ceil(ratio*imageWidth)))
        cv.SaveImage(path+"croppedImage"+str(t0)+".jpg", img)

    #blur the source image to reduce color noise
    cv.Smooth(img, img, cv.CV_BLUR, 3);

    #convert the image to hsv(Hue, Saturation, Value) so its easier to determine the color to track(hue)
    hsv_img = cv.CreateImage(cv.GetSize(img), 8, 3)
    cv.CvtColor(img, hsv_img, cv.CV_BGR2HSV)

    #limit all pixels that don't match our criteria, in this case we are
    #looking for purple but if you want you can adjust the first value in
    #both turples which is the hue range(120,140).  OpenCV uses 0-180 as
    #a hue range for the HSV color model

    distX = [0]*len(colors)
    distY = [0]*len(colors)

    thresholded_img =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
    for h in range(0, len(colors)):
        if (colors[h] == 'red' ):
            cv.InRangeS(hsv_img, (0, 70, 80), (20, 255, 255), thresholded_img)

        if (colors[h] == 'green' ):
            cv.InRangeS(hsv_img, (40, 70, 75), (94, 255, 255), thresholded_img)

        if (colors[h] == 'blue' ):
            cv.InRangeS(hsv_img,  (95, 95, 85), (135, 255, 255), thresholded_img)

        # cv.WaitKey(0)
        #determine the objects moments and check that the area is large enough to be our object
        moments = cv.Moments(cv.GetMat(thresholded_img,1), 0)
        area = cv.GetCentralMoment(moments, 0, 0)


        #there can be noise in the video so ignore objects with small areas
        if(area > 10000):
            #determine the x and y coordinates of the center of the object
            #we are tracking by dividing the 1, 0 and 0, 1 moments by the area
            x_new = cv.GetSpatialMoment(moments, 1, 0)/area
            y_new = cv.GetSpatialMoment(moments, 0, 1)/area
            print colors[h] + ' x: ' + str(x_new) + ' y: ' + str(y_new) + ' area: ' + str(area)

            distX[h] = abs(x_new - xValue)
            distY[h] = abs(y_new - yValue)
            print 'Distance X: ', distX[h], ' Y: ', distY[h]
            areas[h] = int(math.sqrt(distX[h] * distX[h] + distY[h] * distY[h]))

        else:
            distX[h] = -1
            distY[h] = -1
            print colors[h] + ' area ' + str(area)
            print 'Distance X: ', distX[h], ' Y: ', distY[h]

    mlColor = -1
    distances = [0]*(len(colors))
    for i in range(0, len(colors)):
        if distX==-1:
            distances[i] = -1
        else:
            distances[i] = math.sqrt((distX[i] - cv.GetSize(img)[0]/2)**2 + (distY[i]- cv.GetSize(img)[1]/2)**2)
            if mlColor == -1:
                mlColor = i
            else:
                if distances[i] < distances[mlColor]:
                    mlColor = i
        print "Distance to center :", distances[i]

    if mlColor == -1:
        print "No matching color found"
        return -1

    print "Most likely color: ", colors[mlColor]
    return distances.index(mlColor)

if __name__ == '__main__':
    IP = "NAOsIP"
    PORT = 9559
    #naoImage = getColour(IP, PORT)
