from controller import Controller
from connect_to import ConnectToAgent

from KEYBOARD_CONFIG import KEYBOARD_CONFIG_DICT, DEBOUNCE_INTERVAL
from SWARMER_BT_INFO import UUID, ALL_ADDRESSES

conn_agents = [ConnectToAgent(addr, UUID) for addr in ALL_ADDRESSES]

print("Connecting to all swarmers ...")
for agent in conn_agents:
    agent.connect()

# TODO: TEST THIS!
conn_agents = [agent for agent in conn_agents if agent.connected] 
controller = Controller(DEBOUNCE_INTERVAL, KEYBOARD_CONFIG_DICT, conn_agents)
print('Connected to swarmers, ready for commands')
controller.start()
