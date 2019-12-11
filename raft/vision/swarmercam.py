import cv2

class SwarmerCam(object):
	def __init__(self):
		# TODO: Create three of these classifiers, one for each bot
		self.yellow_cascade = cv2.CascadeClassifier("training_results/trained_yellow/cascade.xml") 
		self.orange_cascade = cv2.CascadeClassifier("training_results/trained_orange/cascade.xml") 
		self.blue_cascade = cv2.CascadeClassifier("training_results/trained_blue/cascade.xml") 
		self.video_capture = cv2.VideoCapture(0) # 0 = camera. A path to a video file also works
		vid_cod = cv2.VideoWriter_fourcc(*'XVID')
		self.output = cv2.VideoWriter("videos/cam_video.mp4",
				vid_cod, 20.0, (640,480))
		# Open the camera and get the frame properties 
		vcap = self.video_capture # lazy
		if vcap.isOpened():
			width = vcap.get(cv2.CAP_PROP_FRAME_WIDTH) # float
			height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
			print('Camera width: {}, height: {}'.format(width, height))
		# Note that (0,0) is the top-left of the camera frame
		self.camera_center_x = int(width//2)
		self.camera_center_y = int(height//2)
		self.FAR_AREA = 986
		self.CLOSE_AREA = 20329

	"""
		Takes a frame from the video camera and runs it through the
		cascade classifier trained to detect the leader marker.

		If no leader marker is detected within the frame, None is 
		returned.

		If a leader marker is detected, the classifier returned a
		(x, y, w, h) of a bounding box around the detected leader
		marker (we only use the first box detected). What the 
		function returns in that case is a (x-off, y-off) tuple of
		integers denoting how far off the center of the bounding
		box containing the leader is from the center of the camera
		view. 
		
		- A negative x-off value indicates that the bounding
		box is to the left of the center of the camera view.
		- A negative y-off value indicates that the bounding
		box is above the center of the camera view

		Note that (0,0) in our (and opencv's) view is the 
		top-left of the image frame
	"""
	def pollCameraForBot(self, debug=False):
		# Capture a frame from the camera
		ret, frame = self.video_capture.read()
		camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # TODO: Would non-gray be better?

		res = None
		res = self.pollCascade(frame, camera_image, self.yellow_cascade, debug)
		if res:
		    return res
		res = self.pollCascade(frame, camera_image, self.orange_cascade, debug)
		if res:
		    return res
		res = self.pollCascade(frame, camera_image, self.blue_cascade, debug)
		if res:
		    return res

		# (x offset, y offset, score)
		return res

	# Detect any leader markers in view
	def pollCascade(self, frame, camera_image, cascade_classfier, debug):
		leader_markers = cascade_classfier.detectMultiScale(
				camera_image,
				scaleFactor=1.1, # TODO: 1.1 shrinks/'zooms out' the image
				minNeighbors=4, # TODO: Tune. Smaller = more false positives. Bigger = higher detection threshold
				minSize=(20,20), # TODO: Probably make this bigger since the leader marker won't be that far away
				flags=cv2.CASCADE_SCALE_IMAGE
		)

		res = None
		# (We only use the first marker detected)
		for (x, y, w, h) in leader_markers:
			# Calculate the center of the bounding box
			box_center_x = x + (w//2)
			box_center_y = y + (h//2)
			# Draw the bounding box and center of the bounding box if we're debugging

			if debug:
				cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
				cv2.circle(frame, (box_center_x, box_center_y), 5, (0, 255, 0), 2)
				print("w:{},h:{},A={}".format(w, h, w*h))
			res = (int(box_center_x - self.camera_center_x), 
					int(box_center_y - self.camera_center_y), self.should_move_forward(w, h))
			break

		if debug:
			cv2.circle(frame, (self.camera_center_x, self.camera_center_y), 5, (255,0,0),2)
			# self.output.write(frame)
			cv2.imshow('Video', frame) # TODO: For now we can't turn it off in the code
			cv2.waitKey(1)

		return res

		
	def should_move_forward(self, width, height):
	    area = width * height
	    close_comp = abs(area - self.CLOSE_AREA)
	    far_comp = abs(area - self.FAR_AREA)
	    if close_comp <= far_comp:
	        return True
		
	def __del__(self):
		self.video_capture.release()
		cv2.destroyAllWindows()

# For testing
def main():
	sc = SwarmerCam()
	while True:
		print(sc.pollCameraForBot(debug=True))

if __name__ == '__main__':
	main()
