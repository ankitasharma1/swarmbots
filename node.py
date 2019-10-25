import constants
import config
import socket
import message
from threading import Thread
import helper
import time
import states

# Node class.
class Node():
    def __init__(self, id=0, port=1234):
        # All nodes start in the join state.
        self.state = constants.JOIN
        # All nodes are initialized with the cluster configuration.
        self.config = config.Config()
        self.id = id
        self.port = int(port)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.leader = None
        # For cleaning up purposes.
        self.threads = []
        # <K: node id, V: (ip address, port)>
        self.cluster_info = dict()
        # <K: node id, V: socket>
        self.sockets = dict()
        helper.print_and_flush("Starting node on >>%s<< port %s: %s" %(self.id, self.ip, port))

    # Helper function that will check whether all nodes have joined the cluster.
    def startCluster(self):
        while True:
            # Wait for all nodes to join the cluster.              
            if len(self.cluster_info) == self.config.size:
                helper.print_and_flush("All nodes have joined the cluster")
                # Send start message to all nodes in the cluster.
                for id, socket in self.sockets.items():
                    if id != self.id:
                        socket.send(message.startMessage(self.id, self.cluster_info)) 
                # Wait for some time and enter the follower state.
                time.sleep(self.config.start_timeout)
                states.follower(self)
                return

    # Helper function for handling incoming connections and spawning threads to handle that communication.
    def handleConnections(self):
        # Create socket object.
        s = socket.socket()

        # Update the cluster with our information.
        self.cluster_info.update({self.id: (self.ip, self.port)})

        s.bind(('', self.port))
        helper.print_and_flush("Socket binded to %s" %(self.port))
        # Put the socket into listening mode.
        s.listen(5)
        helper.print_and_flush("Socket is listening")

        while True:
            c, addr = s.accept()
            helper.print_and_flush("Got connection from " + addr[0] + ": " + str(addr[1])) 
            # Start a thread for each socket.
            t = Thread(target=self.listenOnSocket, args=(c,))
            self.threads.append(t)   
            t.start()
        
    # Listen for incoming messages on this socket.
    def listenOnSocket(self, socket):
        size = constants.DATA_SIZE         
        while True:
            try:
                # Deserialize the json into a dict.
                data = message.deserialize(socket.recv(size))

                if data:
                    message_type = data.get(message.TYPE)
                    # Handle request to join the cluster.
                    if message_type == message.JOIN:
                        message_id = data.get(message.ID)
                        # Careful distinctino between joining and rejoining the cluster.
                        if message_id in self.cluster_info.keys():
                            # A node is rejoining the cluster.
                            socket.send(message.startMessage(self.id, self.cluster_info))                             
                        else: 
                            # Joining for the first time.
                            self.sockets.update({data.get(message.ID): socket})
                            self.cluster_info.update({data.get(message.ID): (data.get(message.IP), data.get(message.PORT))})
                    # Message to start.
                    elif message_type == message.START:
                        self.cluster_info = data.get(message.CLUSTER_INFO)
                        self.sockets.update({data.get(message.ID): socket})
                        self.connect()
                else:
                    self.cleanup(socket)
                    return
            except Exception, e: 
                #helper.print_and_flush(str(e))
                self.cleanup(socket)
                return

    # Clean up threads. Close sockets.
    def cleanup(self, socket):
        helper.print_and_flush("Closing socket connection")
        for id, s in self.sockets.items():
            if s == socket:
                del self.sockets[id]
                break
        socket.close()        
        return


    # Join the cluster.
    def join(self, rn):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((rn.ip, rn.port))
        helper.print_and_flush("Connected to %s:%s" %(rn.ip, rn.port))
        # Send request to join cluster message.
        s.send(message.joinMessage(self.id, self.ip, self.port)) 
        # Listen for a 'start' response either when joning for the
        # first time or rejoining the cluster.
        t = Thread(target=self.listenOnSocket, args=(s,))
        self.threads.append(t)   
        t.start()

    # Connect to other nodes in the cluster.
    def connect(self):   
        for id, connection_info in self.cluster_info.items():
            # We don't need to create a connection for ourself and for the
            # node we have already connected to.
            if id != self.id and id not in self.sockets.keys():                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                s.connect((connection_info[0], connection_info[1]))
                helper.print_and_flush("Connected to %s:%s" %(connection_info[0], connection_info[1]))
                self.sockets.update({id: s})
        states.follower(self)                

    # Return list of socket connections to the nodes in the raft cluster known by the current node.
    def getSocketConnections(self):
        return self.sockets


# Remote node class.
class RemoteNode():
    def __init__(self, ip="", port=1234):
        self.ip = ip
        self.port = int(port)
