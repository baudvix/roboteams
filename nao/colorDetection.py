__author__ = 'Lorenz'

import cv

#path = "/Users/Lorenz/Dropbox/Semesterprojekt/roboteams/nao/camImage.png"


#blueMin = [115, 0, 255]
blueMin = [160,100,100]
#blueMax = [0, 210, 255]
blueMax = [190,255,255]

#greenMin = [0, 255, 234]
greenMin = [200,80,80]
#greenMax = [84, 255, 0]
greenMax = [280,255,255]

#yellowMin = [210, 255, 0]
yellowMin = [20,100,100]
#yellowMax = [255, 216, 0]
yellowMax = [30,255,255]

thresholdMin = [blueMin, greenMin, yellowMin]
thresholdMax = [blueMax, greenMax, yellowMax]

# 0 for blue, 1 for green, 2 for yellow
def filterColor(color, image):
    # build pic array - array with all information to the picture
    rgbPic = []
    for i in range(0, width):
        rgbPic.append([])

    # area of pixels within the special threshold
    area = []

    out = ""
    for x in range(0, height):
        for y in range(0, width):
            # get the rgb information of the pixel in x y and add it to the pic array
            s = cv.Get2D(image, x, y)
            RGB = [s[2], s[1], s[0]]
            rgbPic[x].append(RGB)

            # convert RGB to HSV for better threshold
            HSV = RGB2HSV(RGB)
            # see whether the pixel is in the color range
            isColor = isPixelHSVColor(color, HSV)
            # add boolean (0/1) into pic array
            RGB.append(isColor)
            if(isColor):
                #
                area.append([y, x])

            # for print
            out = out +" "+ str(RGB[3])

        print out
        out = ""

    return rgbPic, area

# 0 for blue, 1 for green, 2 for yellow
def isPixelHSVColor(color, HSV):
    # H in threshold range
    if(HSV[0] >= thresholdMin[color][0] and HSV[0] <= thresholdMax[color][0]):
        # S in threshold range
        if(HSV[1] >= thresholdMin[color][1] and HSV[1] <= thresholdMax[color][1]):
            # V in threshold range
            if(HSV[2] >= thresholdMin[color][2] and HSV[2] <= thresholdMax[color][2]):
                return 1

    return 0

def RGB2HSV(RGB):
    R = RGB[0]
    B = RGB[1]
    G = RGB[2]

    H = 0
    S = 0
    V = max(R, G, B)

    if(V != 0):
        S = (V-min(R,G,B))*255/V

    if(V == R and S != 0):
        H = (G - B)*60/S
    elif(V == G and S != 0):
        H = 180+(B - R)*60/S
    elif(V == B and S != 0):
        H = 240+(R - G)*60/S

    if(H<0):
        H=H+360

    return [H, S, V]

# this method gives back the ratio of zero to one in a certain field of pixel
def zeroOneRatio(arrayOfPixels, fieldCentrePixel, fieldSizeXY):
    xMin = fieldCentrePixel[0] - fieldSizeXY/2.
    xMax = fieldCentrePixel[0] + fieldSizeXY/2.
    yMin = fieldCentrePixel[1] - fieldSizeXY/2.
    yMax = fieldCentrePixel[1] + fieldSizeXY/2.
    print str(xMin), str(xMax), str(yMin), str(yMax)

    numberOfPixelInside = 0.
    for i in range(0, len(arrayOfPixels)):
        if(arrayOfPixels[i][0] >= xMin and arrayOfPixels[i][0] <= xMax and arrayOfPixels[i][1] >= yMin and arrayOfPixels[i][1] <= yMax):
            numberOfPixelInside = numberOfPixelInside + 1

    # Prozentanteil des Markers im Rechteck
    percentage = 1 - 0.55
    pixelOfHoleField = fieldSizeXY * fieldSizeXY * percentage
    return numberOfPixelInside/pixelOfHoleField

def colorDetection(color):
    path = "/Users/Lorenz/Documents/Studium/Semesterprojekt/NAO/ColoredMarkers/#1bc543_.png"

    image = cv.LoadImageM(path)
    height = image.height
    width = image.width
    step = image.step
    channels = image.channels

########

hsv = cv.CreateImage(cv.GetSize(image), 8, 3)
thr = cv.CreateImage(cv.GetSize(image), 8, 1)

xColoredPixel = filterColor(1, image)[1]
print xColoredPixel
print zeroOneRatio(xColoredPixel, [35, 29], 20)