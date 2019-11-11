import keyboard
from time import time

class Controller():
    def __init__(self, debounce_interval, keyboard_config_dict, conn_agents):
        # how often should commands be sent
        #   NOTE: these values are in seconds, the debounce_interval should be
        #         roughly equal to RUN_TIME defined in the MotorDriver class
        self.debounce_interval = debounce_interval
        self.last_press = 0.0

        # keyboard_config_dict should be a dictionary with the following keys
        # this decides which keys are listened for and what messages they send
        self.right = keyboard_config_dict['RIGHT']
        self.left = keyboard_config_dict['LEFT']
        self.forward = keyboard_config_dict['FORWARD']
        self.backward = keyboard_config_dict['BACKWARD']

        # ConnectToAgent instances in which to send messages, this could also
        # be a list of sockets or a single socket. All it needs is a `send` 
        # function that can take strings
        self.conn_agents = conn_agents

    def start(self, debug=False):
        while True:
            if keyboard.is_pressed(self.forward) and not self.debounce():
                if debug:
                    print("\nForward press detected")
                self.last_press = time()
                for agent in self.conn_agents:
                    agent.send('forward')
            if keyboard.is_pressed(self.right) and not self.debounce():
                if debug:
                    print("\nRight press detected")
                self.last_press = time()
                for agent in self.conn_agents:
                    agent.send('right')
            if keyboard.is_pressed(self.left) and not self.debounce():
                if debug:
                    print("\nLeft press detected")
                self.last_press = time()
                for agent in self.conn_agents:
                    agent.send('left')
            if keyboard.is_pressed(self.backward) and not self.debounce():
                if debug:
                    print("\nBackward press detected")
                self.last_press = time()
                for agent in self.conn_agents:
                    agent.send('backward')

    def debounce(self):
        elapsed_time = time() - self.last_press
        if elapsed_time > self.debounce_interval:
            return False
        else:
            return True
