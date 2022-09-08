# simple python to reset the usb power when requested by the poco lib example
import time
import os

p = os.popen('sudo /usr/sbin/uhubctl -l 1-1 -a 0')
time.sleep(5)
p = os.popen('sudo /usr/sbin/uhubctl -l 1-1 -a 1')
print(p)