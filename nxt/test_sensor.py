import nxt.locator
from nxt.sensor import *

brick = nxt.locator.find_one_brick(host='00:16:53:10:48:E7')
base_sensor = BaseDigitalSensor(brick, PORT_1, False)
info = base_sensor.get_sensor_info()
print "info gelesen ",   str(info)

