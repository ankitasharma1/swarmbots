import keyboard
from time import time

from bt_server import BT_Server
from KEYBOARD_CONFIG import KEYBOARD_CONFIG_DICT, DEBOUNCE_INTERVAL

class Controller():
    def __init__(self):
        # how often should commands be sent
        #   NOTE: these values are in seconds, the debounce_interval should be
        #         roughly equal to RUN_TIME defined in the MotorDriver class
        self.debounce_interval = DEBOUNCE_INTERVAL
        self.last_press = 0.0

        # keyboard_config_dict should be a dictionary with the following keys
        # this decides which keys are listened for and what messages they send
        self.right = KEYBOARD_CONFIG_DICT['RIGHT']
        self.left = KEYBOARD_CONFIG_DICT['LEFT']
        self.forward = KEYBOARD_CONFIG_DICT['FORWARD']
        self.backward = KEYBOARD_CONFIG_DICT['BACKWARD']

        # Run the server. It will be connected to by the leader's client
        controller_addr = BT_CONTROLLER_DICT["CONTROLLER"]["ADDR"]
        controller_port = BT_CONTROLLER_DICT["CONTROLLER"]["PORT"]
        self.server = BT_Server(controller_addr, controller_port)

    def start(self, debug=False):
        while True:
            if keyboard.is_pressed(self.forward) and not self.debounce():
                if debug:
                    print("\nForward press detected")
                self.last_press = time()
                self.server.send('forward')
            if keyboard.is_pressed(self.right) and not self.debounce():
                if debug:
                    print("\nRight press detected")
                self.last_press = time()
                self.server.send('right')
            if keyboard.is_pressed(self.left) and not self.debounce():
                if debug:
                    print("\nLeft press detected")
                self.last_press = time()
                self.server.send('left')
            if keyboard.is_pressed(self.backward) and not self.debounce():
                if debug:
                    print("\nBackward press detected")
                self.last_press = time()
                self.server.send('backward')

    def debounce(self):
        elapsed_time = time() - self.last_press
        if elapsed_time > self.debounce_interval:
            return False
        else:
            return True
