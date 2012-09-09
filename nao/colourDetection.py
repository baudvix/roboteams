import time
import cv
import math
import Image

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

    t0 = time.time()

    # Get a camera image.
    naoImage = camProxy.getImageRemote(videoClient)

    t1 = time.time()

    camProxy.unsubscribe(videoClient)

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    xValue = imageWidth/2
    yValue = imageHeight/2

    # Create a PIL Image from our pixel array.
    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    # Save the image.
    im.save(path+ "/camImage" + str(t0) + ".jpg", "JPEG")

    img = cv.LoadImage(path+"camImage" + str(t0) + ".jpg")

    centerX = imageWidth/2
    centerY = imageHeight/2

    ratio = math.ceil(markerSize/0.6)
    topLeftCropCorner = [centerX-ratio * imageWidth * 0.5, centerY-ratio * imageWidth * 0.5]
    bottomRightCropCorner = topLeftCropCorner + [ratio*imageWidth, ratio*imageHeight]

    # crop the image if possible
    if(not(topLeftCropCorner < [0,0] or bottomRightCropCorner > [imageWidth,imageHeight])):
        cv.SetImageROI(img, (topLeftCropCorner[0], topLeftCropCorner[1], ratio*imageWidth, ratio*imageHeight))
        cv.SaveImage(path+"/croppedImage"+str(t0)+".jpg", img)

    #blur the source image to reduce color noise
    cv.Smooth(img, img, cv.CV_BLUR, 3);

    #convert the image to hsv(Hue, Saturation, Value) so its easier to determine the color to track(hue)
    hsv_img = cv.CreateImage(cv.GetSize(img), 8, 3)
    cv.CvtColor(img, hsv_img, cv.CV_BGR2HSV)

    #limit all pixels that don't match our criteria, in this case we are
    #looking for purple but if you want you can adjust the first value in
    #both turples which is the hue range(120,140).  OpenCV uses 0-180 as
    #a hue range for the HSV color model
    thresholded_img =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
    for h in range(0, len(colors)):
        if (colors[h] == 'red' ):
            cv.InRangeS(hsv_img, (0, 70, 80), (20, 255, 255), thresholded_img)

        if (colors[h] == 'green' ):
            cv.InRangeS(hsv_img, (40, 85, 80), (75, 255, 255), thresholded_img)

        if (colors[h] == 'blue' ):
            cv.InRangeS(hsv_img,  (95, 90, 80), (135, 255, 255), thresholded_img)

        cv.WaitKey(0)
        #determine the objects moments and check that the area is large enough to be our object
        moments = cv.Moments(cv.GetMat(thresholded_img,1), 0)
        area = cv.GetCentralMoment(moments, 0, 0)

        #there can be noise in the video so ignore objects with small areas
        if(area > 20000):
            #determine the x and y coordinates of the center of the object
            #we are tracking by dividing the 1, 0 and 0, 1 moments by the area
            x_new = cv.GetSpatialMoment(moments, 1, 0)/area
            y_new = cv.GetSpatialMoment(moments, 0, 1)/area
            print colors[h] + ' x: ' + str(x_new) + ' y: ' + str(y_new) + ' area: ' + str(area)

            distX[h] = abs(x_new - xValue)
            distY[h] = abs(y_new - yValue)
            print 'Distance X: ', distX, ' Y: ', distY
            areas[h] = int(math.sqrt(distX * distX + distY * distY))

        else:
            print colors[h] + ' area ' + str(area)

        nearestColor = 0
        distances = []
        for i in range(0, len(colors)-1):
            distances[i] = math.sqrt(math.pow(distX[i] - cv.GetSize(img)[0],2) + math.pow(distY[i] - cv.GetSize(img)[1],2))

        print "Most likely color: ", colors[distances.index(min(distances))]
        return distances.index(min(distances))

if __name__ == '__main__':
    IP = "NAOsIP"
    PORT = 9559
    #naoImage = getColour(IP, PORT)
