#from naoqi import ALProxy
#memoryProxy = ALProxy("ALMemory", "194.95.174.188", 9559)
#arrayOfMarker = memoryProxy.getData("LandmarkDetected")
#print arrayOfMarker

imageWidth = 640
imageHeight = 460
topLeftCropCorner = [1000,0]

if(topLeftCropCorner < [0,0] or topLeftCropCorner > [imageWidth,imageHeight]):
    print "no!"
