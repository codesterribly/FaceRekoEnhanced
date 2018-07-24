#!/usr/bin/env python

from picamera import PiCamera
import time
import os

count = 3
camera = PiCamera()
#camera.vflip = True
#camera.hflip = True

print '[+] A photo will be taken in 3 seconds...'

for i in range(count):
    print (count - i)
    time.sleep(1)

#milli = int(round(time.time() * 1000))
image = 'selfie.jpg'
camera.capture(image)
print 'Your image was saved to %s' % image
