import sys
from naoqi import ALProxy

#if (len(sys.argv) < 2):
#    print "Usage: 'python motion_getangles.py IP [PORT]'"
#    sys.exit(1)

#IP = sys.argv[1]
IP = "194.95.174.164"
PORT = 9559
if (len(sys.argv) > 2):
    PORT = sys.argv[2]
try:
    proxy = ALProxy("ALMotion", IP, PORT)
except Exception,e:
    print "Could not create proxy to ALMotion"
    print "Error was: ",e
    sys.exit(1)

# Example that finds the difference between the command and sensed angles. 
names  = "Body" 
useSensors  = False 
commandAngles = proxy.getAngles(names, useSensors)
print "Command angles: " + str(commandAngles)
useSensors  = True 
sensorAngles = proxy.getAngles(names, useSensors)
print "Sensor angles: " + str(sensorAngles)
errors = [] 
for i in range(0, len(commandAngles)): 
  errors.append(commandAngles[i]-sensorAngles[i]) 
print "Errors", errors