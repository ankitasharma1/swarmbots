import yaml
import sys
from node import Node

CONFIG_FILE = 'config.yaml'

def main():
    # Check command line arguments.
    if len(sys.argv) != 2:
        print('usage: main.py [id]')            
        return

    # Unique node id.
    node_id = int(sys.argv[1])

    with open(CONFIG_FILE, 'r') as f:
        doc = yaml.load(f)

    nodes = doc['nodes']
    cluster_info = dict()
    n = None

    for id in nodes:
        address = nodes[id]['address']
        port = nodes[id]['port']
        if id == node_id:
            n = Node(id, address, port)
        else:
            cluster_info.update({id : (address, port)})

    # The node is aware of how to connect to other nodes in the cluster.
    n.cluster_info = cluster_info
    # Node 'init' routine.
    n.init()   

main()
