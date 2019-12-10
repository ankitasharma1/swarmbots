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
        self.last_time = 0.0

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        while self.on:
            if not self.debounce():
                # If a leader marker is detected, classifier returns
                # (x-off, y-off) negative x-off: left, negative y-off: above the center
                res = self.swarmer_cam.pollCameraForBot()
                if res:
                    x_coord = res[0]
                    if x_coord < 0:
                        self.motor.orient_left()
                    elif x_coord > 0:
                        self.motor.orient_right()
                self.last_time = time()
    
    def stop(self, testing=False):
        # testing allows stopping and starting without killing the conn
        self.on = False
        sleep(0.15)
        self.motor.stop()
        if not testing:
            self.client.clean_up()

    def debounce(self):
        elapsed_time = time() - self.last_time
        if elapsed_time > RUN_TIME:
            return False
        else:
            return True            
    

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

