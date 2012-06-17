
import nxt.locator
from nxt.sensor import *

b = nxt.locator.find_one_brick(host='00:16:53:10:48:F3')
us = Ultrasonic(b, PORT_1)
touch = Touch(b, PORT_2)
while True:
	if touch.get_sample() == 1:
		print 'ultrasonic: ', us.get_sample()
