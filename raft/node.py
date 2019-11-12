import sys
import threading
from threading import Thread
import socket
import time

"""
Cluster Info
"""
CLUSTER_SIZE = 3
NUM_EXT_CONNS = 2

"""
Commands
"""
EXIT = 'exit'
HELP = 'h'
CLUSTER_INFO = 'c'

"""
States
"""
JOIN = 'join'
FOLLOWER = 'follower'
CANDIDATE = 'candidate'
LEADER = 'leader'

class Node():
    def __init__(self, id, address, port):
        print("Creating node %d " %(id))
        self.id = id
        self.address = address
        self.port = port
        self.state = JOIN
        self.cluster_info = None
        # Basic synchronization is required to kep track of alive/closed sockets.
        self.sockets_lock = threading.Lock()
        self.sockets = dict()

    def init(self):
        """
        Waits until the cluster is fully connected to initiate raft.
        """
        start_raft_thread = Thread(target=self.start_raft, args=())
        start_raft_thread.setDaemon(True)
        start_raft_thread.start()        

        """
        Kick off serving the remote controller thread.
        """
        service_remote_thread = Thread(target=self.service_remote, args=())
        service_remote_thread.setDaemon(True)
        service_remote_thread.start()        

        """
        Kick off serving incoming connections thread.
        """
        service_incoming_conns_thread = Thread(target=self.service_incoming_conns, args=())
        service_incoming_conns_thread.setDaemon(True)
        service_incoming_conns_thread.start()        

        """
        Kick off connecting to the rest of the cluster thread.
        """
        connect_thread = Thread(target=self.connect, args=())
        connect_thread.setDaemon(True)
        connect_thread.start()        

        """
        Kick off REPL.
        """
        self.service_repl() 
      
    def start_raft(self):
        while True:
            if len(self.sockets) == NUM_EXT_CONNS:
                time.sleep(2)
                print(">> Start RAFT")
                # TODO: do_follower(self)
                return

    def service_remote(self):
        print("Service commands from the remote.")
        while True:
            pass

    def service_incoming_conns(self):
        print("Service incoming connections.")
        s = socket.socket()
        s.bind(('', self.port))
        print("Socket binded to %s" %(self.port))
        # Put the socket into listening mode.
        s.listen(5)
        print("Socket is listening")
        while True:
            c, addr = s.accept()
            # Start a thread for each socket.
            t = Thread(target=self.listen_on_socket, args=(c,))
            t.setDaemon(True)
            t.start()

    def connect(self):
        print("Connect to rest of the cluster.")
        while True:
             for id, connection_info in self.cluster_info.items():
                  if id != self.id: 
                     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                     try:
                         s.connect((connection_info[0], connection_info[1]))
                         self.sockets.update({id: s})
                         t = Thread(target=self.listen_on_socket, args=(s,))
                         t.setDaemon(True)
                         t.start()                
                         if len(self.sockets) == NUM_EXT_CONNS:
                              return
                     except Exception, e:
                         s.close()

    def listen_on_socket(self, socket):
        pass

    def service_repl(self):
        print("Service Incoming connections.")
        while True:
            commands = sys.stdin.readline().split()
            if len(commands) > 0:
                command = commands[0]
                if command == HELP:
                    print("exit: %s" %(EXIT))
                elif command == CLUSTER_INFO:
                    print(self.cluster_info)
                elif command == EXIT:
                    print("Goodbye!")
                    return
                else:
                    continue
            else:
                print("Unsupported command. For list of supported commands type 'h'")



