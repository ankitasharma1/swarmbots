from threading import Thread
import time
import random

from vision.swarmercam import SwarmerCam

from communication.SWARMER_ID import SWARMER_ID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME
from rssi_handler import RssiHandler


# This file should be run on the bot and connect to the server running on the
# the controller
class FollowerDriving:
    def __init__(self):
        self.motor = MotorDriver(THROTTLE / 1.3)
        self.rssi_handler = RssiHandler(SWARMER_ID)
        self.on = False
        self.swarmer_cam = SwarmerCam()

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
                should_drive = res[2]
                print(f"should drive? {should_drive}")

                if self.am_i_oriented(x_offset):
                    print("oriented!")
                    # We are far away from something in view.
                    if should_drive:
                        if self.rssi_handler.am_i_close():
                            print("doing random backoff")
                            self.random_backoff()
                        print("driving forward")
                        self.motor.forward()
                        time.sleep(1)
                        self.motor.stop()
            else:
                print("not oriented")
                self.orient()

    def random_backoff(self):
        random.seed(int(SWARMER_ID[1]))
        time.sleep(random.randrange(0, 4))

    def am_i_oriented(self, x_offset):
        if abs(x_offset) < 100:
            return True
        return False

    def orient(self):
        while True:
            res = self.swarmer_cam.pollCameraForBot()
            if res:
                x_offset = res[0]                
                if self.am_i_oriented(x_offset):
                    break
                # Left
                if x_offset < 0:
                    self.motor.orient_left()
                    time.sleep(0.25)
                # Right
                else:
                    self.motor.orient_right()
                    time.sleep(0.25)
                self.motor.stop()
            else:
                self.motor.orient_right()
                time.sleep(0.25)
                self.motor.stop()

    def stop(self):
        # testing allows stopping and starting without killing the conn
        self.on = False
        time.sleep(0.1)
        self.motor.stop()

