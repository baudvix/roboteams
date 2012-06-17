import sys
import time
#LEGO
import nxt.direct
from nxt.brick import Brick, FileFinder
from nxt.locator import find_one_brick
from nxt.locator import Method

TURN_POWER = 40
TURN_ADJUSTMENT = 2.08

class Explorer():
    def __init__(self, mac):
        self.brick = find_one_brick(host=mac, method=Method(usb=False, bluetooth=True))
        
    def __del__(self):
        pass
        
    def turnright(self, degrees):
        pass
    
    def turnleft(self,  degrees):    
        pass
        
    def go_forward(self, distance):
        pass
        
    def go_back(self, distance):
        pass
    
    def find_programs(self):
        ff = FileFinder(robo.brick, "*.rxe")
        for f in ff:
            print(f)
    
    def test_app(self, app):
        self.brick.start_program(app)

if __name__ == '__main__':
    print("suche robo")
    robo = Explorer(mac="00:16:53:10:48:F3")
    if robo != None: 
        print("robo gefunden")
    else: 
        print("no robo")
        sys.exit()
    #print(str(robo.brick.get_device_info()))
    #robo.find_programs()
    robo.test_app("bt_test.rxe")
    print("BT sende...")
    robo.brick.message_write(5, 'Testnachricht')
    print("BT sende fertig!")
    time.sleep(5)
    print("BT empfange...")
    for i in range(200):
        try:
            local_box, message = robo.brick.message_read(11, 11, True)
            print(local_box, message)
        except:
            pass

    print("fertig")
