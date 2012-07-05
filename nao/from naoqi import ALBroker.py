from naoqi import ALBroker
from naoqi import ALProxy

def main():
	myBroker = ALBroker("myBroker","0.0.0.0",0,"germanopen3.local",9559)
	motion = ALProxy("ALMotion")
    tracker = ALProxy("ALRedBallTracker")
    tracker.stopTracker()

if __name__ == '__main__':
	main()