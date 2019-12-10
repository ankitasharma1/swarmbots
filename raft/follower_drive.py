from threading import Thread
from time import time

from communication.SWARMER_ID import SWARMER_ID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME


# This file should be run on the bot and connect to the server running on the
# the controller
class FollowerDriving:
    def __init__(self, debug=False):
        self.motor = MotorDriver(THROTTLE)
        self.on = False

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        #while self.on:
        pass
    
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

