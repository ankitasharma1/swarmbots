import node
import constants
import sys
from threading import Thread

# Global node.
n = None

def main():
    # Check command line arguments.
    if len(sys.argv) != constants.CLUSTER_INITIATOR_CMDS and len(sys.argv) != constants.JOINING_CLUSTER_CMDS:
        print('usage: start.py [id] [port] or start.py [id] [port] [ip address] [port]')            
        return

    # Error check the pass in port numbers.
    if not sys.argv[2].isdigit() and not sys.argv[4].isdigit():
        print('usage: start.py [port] or start.py [port] [ip address] [port]')            
        return        

    # Create a node.    
    id = sys.argv[1]
    port = sys.argv[2]
    n = node.Node(id, port)
    # Handle incoming connections.    
    thread = Thread(target=n.handleConnections, args=())
    thread.start()
    if len(sys.argv) == constants.JOINING_CLUSTER_CMDS:
        rn = node.RemoteNode(sys.argv[3], sys.argv[4])
        # Request for node to join or rejoinn the cluster.
        n.join(rn)
    else:
        start = Thread(target=n.startCluster, args=())
        start.start()
main()