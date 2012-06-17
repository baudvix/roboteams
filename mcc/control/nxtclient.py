from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from mccserver import SendData, ArrivedPoint, GetTag

import time
import threading
import Queue

class NXTClient(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self, inq, outq):
        self.robotype = 0
        self.run_cmd()
        self.inqueue = inq
        self.outqueue = outq
        reactor.run(installSignalHandlers=0)

    def put_cmd(self, *args, **kw):
        self.outqueue.put((args, kw))

    def get_cmd(self):
        print 't'

    def run_cmd(self):
        reactor.callLater(0.5, self.run_cmd)
        item = self.outqueue.get()
        if isinstance(item[0], SendData):
            cmd_data(item[0], item[1])


    def cmd_init(self, robotype):
        d = ClientCreator(reactor, amp.AMP).connectTCP(
            '127.0.0.1', 1234).addCallback(
                lambda p: p.callRemote(GetTag, robotype=robotype)).addCallback(
                    lambda result: result['tag'])
        def done(result):
            print 'Done with init:', result
        d.addCallback(done)

    def cmd_data(self, *args, **kw):
        d = ClientCreator(reactor, amp.AMP).connectTCP(
            '127.0.0.1', 1234).addCallback(
                lambda p: p.callRemote(args, kw)).addCallback(
                    lambda result: result['OK'])
        def done(result):
            print 'Done with data: ', result
        d.addCallback(done)

    def cmd_arrived(self, x, y):
        d = ClientCreator(reactor, amp.AMP).connectTCP(
            '127.0.0.1', 1234).addCallback(
                lambda p: p.callRemote(ArrivedPoint, x=x, y=y))
        def done(result):
            print 'Done with arrived:', result
        d.addCallback(done)

if __name__ == '__main__':
    nxtclient = NXTClient()
    nxtclient.start()
    print 'x'
    nxtclient.put_cmd(SendData, {'pointTag': 1, 'x':1, 'y':1, 'yaw':1})