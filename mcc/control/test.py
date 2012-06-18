from twisted.internet import reactor
import random

def loopPrinting():
    print chr(random.randint(97, 122))
    reactor.callLater(1.0, loopPrinting)

loopPrinting()
reactor.run()