from naoqi import ALProxy
memoryProxy = ALProxy("ALMemory", "194.95.174.172", 9559)
arrayOfMarker = memoryProxy.getData("LandmarkDetected")
print arrayOfMarker
