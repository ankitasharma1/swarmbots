# NOTE: This must be run as admin because the keyboard library is bullshit

from communication.controller import Controller
from communication.connect_to import ConnectToAgent
from communication.KEYBOARD_CONFIG import KEYBOARD_CONFIG_DICT, DEBOUNCE_INTERVAL
from communication.SWARMER_BT_INFO import UUID, ALL_ADDRESSES

conn_agents = [ConnectToAgent(addr, UUID) for addr in ALL_ADDRESSES]

print("Connecting to all swarmers ...")
for agent in conn_agents:
    agent.connect()

conn_agents = [agent for agent in conn_agents if agent.connected]
if not conn_agents:
    print("ERROR: Couldn't establish connection with any swarmer")
else:
    controller = Controller(DEBOUNCE_INTERVAL, KEYBOARD_CONFIG_DICT, conn_agents)
    print('Connected to swarmers, ready for commands')
    controller.start()
