from threading import Thread, Lock

from communication.bt_client import BT_Client
from communication.BT_CONFIG import BT_ADDR_DICT, BT_CONTROLLER_DICT
from communication.SWARMER_ID import SWARMER_ID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME, MSG_SIZE

# This file should be run on the bot and connect to the server running on the
# the controller
class LeaderDriving():
    def __init__(self, debug=False):
        self.motor = MotorDriver(THROTTLE, RUN_TIME)
        self.client = BT_Client(SWARMER_ID, debug) 
        
        controller_addr = BT_CONTROLLER_DICT["CONTROLLER"]["ADDR"]
        controller_port = BT_CONTROLLER_DICT["CONTROLLER"]["PORT"]
        self.client.connect(controller_addr, controller_port)

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        while self.on:
            cmd = self.client.recv(msg_timeout=0.2)
            if cmd == 'forward':
                self.motor.forward()
            if cmd == 'backward':
                self.motor.backward()
            if cmd == 'right':
                self.motor.right()
            if cmd == 'left':
                self.motor.left()
    
    def stop(self, testing=False):
        # testing allows stopping and starting without killing the conn
        self.on = False
        if not testing:
            self.client.clean_up()

if __name__ == '__main__':
    from time import sleep
    
    l = LeaderDriving(True)
    print("driving")
    l.drive()
    sleep(120)
    print("stopping for testing")
    l.stop(True)
    sleep(20)
    print("driving")
    l.drive()
    sleep(60)
    print("stopping and cleaning up")
    l.stop()
    print("goodbye")

