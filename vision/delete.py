import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (800, 800)
    camera.start_preview()
    time.sleep(300)
    camera.capture('foo.jpg')
