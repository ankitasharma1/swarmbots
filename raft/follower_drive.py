from threading import Thread
from time import time

from vision.swarmercam import SwarmerCam

from communication.SWARMER_ID import SWARMER_ID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME
from rrsi_handler import RssiHandler
import random

# This file should be run on the bot and connect to the server running on the
# the controller
class FollowerDriving:
    def __init__(self, debug=False):
        self.motor = MotorDriver(THROTTLE)
        self.rssi_handler = RssiHandler(SWARMER_ID)
        self.on = False
        self.swarmer_cam = SwarmerCam("blue", "orange", "yellow")

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        while self.on:
            res = None
            # Poll for swarm a few times before making any decisions.
            for _ in range(3):
                res = self.swarmer_cam.pollCameraForBot()
                # If we detect the swarm, break.
                if res:
                    break
            
            # The swarm is in view.
            if res:
                x_offset = res[0]
                y_offset = res[1]
                should_drive = res[2]

                if self.am_i_oriented(x_offset):
                    # We are far away from something in view.
                    if should_drive:
                        if self.rssi_handler.am_i_close():
                            self.random_backoff()
                        self.motor.forward()
                        time.sleep(0.5)
                        self.motor.stop()
                else:
                   self.orient()

    def random_backoff(self):
        seed = rand.seed(int(SWARMER_ID[1]))
        time.sleep(random.randrange(0, 4))

    def am_i_oriented(self, x_offset):
        if abs(x_offset) < 20:
            return True
        return False

    def orient(self):
        while True:
            res = self.swarmer_cam.pollCameraForBot()
            if res:
                x_offset = res[0]                
                if am_i_oriented(x_offset):
                    break
                # Left
                if x_offset < 0:
                    self.motor.orient_left()
                    time.sleep(0.5)
                # Right
                else:
                    self.motor.orient_right()
                    time.sleep(0.5)
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

