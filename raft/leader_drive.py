from threading import Thread
from time import time

from communication.bt_client import BT_Client
from communication.BT_CONFIG import BT_ADDR_DICT, BT_CONTROLLER_DICT
from communication.SWARMER_ID import SWARMER_ID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME


# This file should be run on the bot and connect to the server running on the
# the controller
class LeaderDriving:
    def __init__(self, debug=False):
        self.motor = MotorDriver(THROTTLE)
        self.client = BT_Client(SWARMER_ID, debug) 
        
        controller_addr = BT_CONTROLLER_DICT["CONTROLLER"]["ADDR"]
        controller_port = BT_CONTROLLER_DICT["CONTROLLER"]["PORT"]
        self.client.connect(controller_addr, controller_port)

        self.last_press = 0.0
        self.on = False

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        while self.on:
            cmd = self.client.recv(msg_timeout=0.15)
            if not self.debounce():
                if cmd == None:  # this has to be None else it will match b' '
                    self.motor.stop()
                if cmd == 'forward':
                    self.motor.forward()
                if cmd == 'backward':
                    self.motor.backward()
                if cmd == 'right':
                    self.motor.right()
                if cmd == 'left':
                    self.motor.left()
                self.last_press = time()
                print(f"Command {cmd}")
    
    def stop(self, testing=False):
        # testing allows stopping and starting without killing the conn
        self.on = False
        sleep(0.15)
        self.motor.stop()
        if not testing:
            self.client.clean_up()
    
    def debounce(self):
        elapsed_time = time() - self.last_press
        if elapsed_time > RUN_TIME:
            return False
        else:
            return True


if __name__ == '__main__':
    from time import sleep
    
    l = LeaderDriving(True)
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

