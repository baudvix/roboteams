#from naoqi import ALProxy
#memoryProxy = ALProxy("ALMemory", "194.95.174.188", 9559)
#arrayOfMarker = memoryProxy.getData("LandmarkDetected")
#print arrayOfMarker

import time
from naoqi import ALProxy

IP = "194.95.174.188"
PORT = 9559
aup = ALProxy("ALAudioPlayer", IP, PORT)

#Loads a file and launchs the playing 5 seconds later
fileId = aup.loadFile("/home/nao/what shall we do with the drunken sailor2.0_5min.wav")
time.sleep(1)
aup.play(fileId)
