from naoqi import ALProxy

try:
  motion = ALProxy("NaoWalk","194.95.174.145",9559)
  motion.retrieveBall()

except RuntimeError,e:
	print e