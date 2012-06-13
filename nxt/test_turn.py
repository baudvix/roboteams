from neu import Explorer
from time import sleep

print "Dreirad ermitteln"
nxt = Explorer('00:16:53:10:48:F3')
for i in range(10):
    print "%d rechts drehen" % (i+1)
    nxt.turnright(360)

sleep(10)

for i in range(10):
    print "%d links drehen" % (i+1)
    nxt.turnleft(360)
