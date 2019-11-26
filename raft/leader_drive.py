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
        client.connect(controller_addr, controller_port)

    def drive(self):
        self.on = True
        t = Thread(target=self._drive)
        t.setDaemon(True)
        t.start()

    def _drive(self):
        while self.on:
            cmd = self.client.recv(msg_timeout=0.2)
            if cmd == 'forward':
                md.forward()
            if cmd == 'backward':
                md.backward()
            if cmd == 'right':
                md.right()
            if cmd == 'left':
                md.left()
    
    def stop(self):
        self.on = False
        self.client.clean_up()
