import NaoWalk

# n = NaoWalk()
# n.motion.walkInit()
# n.retrieveBall()
# n.walkUpToBall()

from naoqi import ALProxy

proxy = ALProxy("NaoWalk", "194.95.174.150", 9559)
proxy.retrieveBall()