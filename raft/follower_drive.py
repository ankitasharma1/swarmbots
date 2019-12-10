from threading import Thread
from time import time

from vision.swarmercam import SwarmerCam

from communication.SWARMER_ID import SWARMER_ID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME

# This file should be run on the bot and connect to the server running on the
# the controller
class FollowerDriving:
    def __init__(self, debug=False):
        self.motor = MotorDriver(THROTTLE)
        self.on = False
        self.swarmer_cam = SwarmerCam("blue", "orange", "yellow")

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        while self.on:
            # Get score from RSSI.
            rssi_score = get_rssi_score()
            # Too Close.
            if rssi_score == 1:
                self.motor.backward()
            # Too Far.
            if rssi_score == 3:
                # Orient.
                i = 0
                while i < 3:
                    res = self.swarmer_cam.pollCameraForBot()
                    x_coord = res[0]
                    # Left
                    if x_coord < 0:
                        self.motor.orient_left()
                    # Right
                    else:
                        self.motor.orient_right()
                    i += 1
            time.sleep(5)
            self.motor.stop()
    
    def stop(self, testing=False):
        # testing allows stopping and starting without killing the conn
        self.on = False
        sleep(0.15)
        self.motor.stop()
        if not testing:
            self.client.clean_up()
    

if __name__ == '__main__':
    from time import sleep
    
    l = FollowerDriving(True)
    print("driving")
    l.drive()
    sleep(60)
    print("stopping for testing")
    l.stop(True)
    sleep(20)
    print("driving")
    l.drive()
    sleep(60)
    print("stopping and cleaning up")
    l.stop()
    print("goodbye")

