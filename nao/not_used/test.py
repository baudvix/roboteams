from naoqi import ALProxy

IP = "194.95.174.187"
PORT = 9559

def startSensorProxy():
    # Create a proxy to Motion
    try:
        sensorProxy = ALProxy("ALSensorsProxy", IP, PORT)
    except Exception, e:
        print "Error when creating sensor proxy: "
        print str(e)
        exit(1)
    return sensorProxy

#sensorProxy = startSensorProxy()

def startMemoryProxy():
    # Create a proxy to ALMemory
    try:
        memoryProxy = ALProxy("ALMemory", IP, PORT)
    except Exception, e:
        print "Error when creating memory proxy: "
        print str(e)
        exit(1)
    return memoryProxy

handBefore = startMemoryProxy.getData("FrontTactilTouched")
print handBefore

if(sensorProxy.FrontTactilTouched() or sensorProxy.FrontTactilTouched() or sensorProxy.FrontTactilTouched()):
    print "yeaah"