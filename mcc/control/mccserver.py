from twisted.protocols import amp
from command import GetTag, SendData, ArrivedPoint, NxtCalibrated

class Server():

    def __init__(self):
        

#Protocol
class RoboProtocol(amp.AMP):

    def get_tag(self, robotype):
        print 'Got a new robo: type=%d' %(robotype)
        return {'tag': 0}
    GetTag.responder(get_tag)

    def send_data(self, pointTag, x, y, yaw):
        print 'Send data %d: (%d, %d, %d)' % (pointTag, x, y, yaw)
        return{'OK': 'data is used'}
    SendData.responder(send_data)

    def arrived_point(self, x, y):
        print 'Arrived at (%d. %d)' % (x, y)
        return {'OK': 'arrival is noticed'}
    ArrivedPoint.responder(arrived_point)

    def nxt_calibrated(self, nxttag, x, y, yaw):
        print 'NXT calibrated #%d (%d, %d, %d)' %(nxttag, x, y, yaw)
        return {'OK': 'thanks for calibration'}
    NxtCalibrated.responder(nxt_calibrated)

    def nxt_spotted(self, nxttag):
        print 'spotted NXT #%d' %(nxttag)
        return {'OK': 'NXT is back home'}
    NxtSpotted.responder(nxt_spotted)

def main():
    from twisted.internet import reactor
    from twisted.internet.protocol import Factory
    pf = Factory()
    pf.protocol = RoboProtocol
    reactor.listenTCP(1234, pf)
    print 'started'
    reactor.run()

if __name__ == '__main__':
    main()