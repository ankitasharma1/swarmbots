import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import sys
import os

if len(sys.argv) < 2:
	print("Usage: {} <dest_dir>".format(sys.argv[0]))
	sys.exit(1)

destDir = os.path.join(sys.argv[1])
if not os.path.exists(destDir):
        os.makedirs(destDir)

camera = PiCamera()
camera.resolution = (640, 480) # Too big = choppy 
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)


# This first loop is to give us time to orient the camera
# bgr saves the video into numpy array with a channel order of Blue-Green-Red
# use_video_port treats the stream as video
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# Numpy array representing the image
	# frame.array = numpyarr of (width, height, Blue/Green/Red)
	image = frame.array

	cv2.imshow("Waiting...", image)
	# Wait at least 1 ms for a key press, otw return -1
	# This is to negate the effects of key-modifiers (Shift, Ctrl, Alt, etc)
	# which (apparently?)set bit above the first two Least-Siginificant-Bytes 
	# on certain platforms
	key = cv2.waitKey(1) & 0xFF
	# key = cv2.waitKey(1)
	# print(key)
	# Clear stream in preparation for the next frame
	rawCapture.truncate(0)

	if key == ord("q"):
		# So we don't have two windows onscreen
		cv2.destroyAllWindows()
		break


# The code is basically the same as the above, except we're saving the video into
# enumerated images
camera.start_preview()
try:
	for filename in camera.capture_continuous(os.path.join(destDir,'img{counter:03d}.jpg'), format="jpeg", use_video_port=True):
		print(filename)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			cv2.destroyAllWindows()
			break
finally:
	camera.stop_preview()
