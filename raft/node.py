import sys
import threading
from threading import Thread
import socket
import time

from communication.server import Server
from communication.client import Client

from WIFI_CONFIG import WIFI_DICT

"""
Cluster Info
"""
CLUSTER_SIZE = 3
NUM_EXT_CONNS = 2

"""
Commands
"""
EXIT = 'e'
HELP = 'h'
STATE = 's'

"""
States
"""
JOIN = 'join'
FOLLOWER = 'follower'
CANDIDATE = 'candidate'
LEADER = 'leader'

class Node():
    def __init__(self, swarmer_id):
        print(f"Creating Node: {swarmer_id}")
        self.swarmer_id = swarmer_id
        self.state = JOIN

        # Basic synchronization is required to kep track of alive/closed sockets.
        self.server_threads = []
        self.client_threads = []
        self.server_lock = threading.Lock()
        self.client_lock = threading.Lock()

        # Message queues, needs locking in each server thread
        self.incoming_messages = [[] for _ in range(len(WIFI_DICT))]
        self.outgoing_messages = [[] for _ in range(len(WIFI_DICT))]

    def init(self):
        self.service_incoming_conns()
        self.service_outgoing_conns()

        """
        Kick off REPL.
        """
        self.service_repl() 

    def send_to(self, client_id_list, msg):
        for c_id in client_id_list:
            if c_id == self.swarmer_id:
                continue
            shared_q_index = WIFI_DICT[c_id]['shared_q_index']
            self.client_lock.acquire()
            self.outgoing_messages[shared_q_index].append(msg)
            self.client_lock.release()

    def recv_from(self, server_id_list):
        for s_id in server_id_list:
            if s_id == self.swarmer_id:
                continue
            shared_q_index = WIFI_DICT[s_id]['shared_q_index']
            self.server_lock.acquire()
            msg = self.incoming_messages[shared_q_index].pop(0)
            self.server_lock.release()
            print(f"Received msg from {s_id}: {msg}")

    def service_outgoing_conns(self):
        print("Establishing outgoing connections")
        for k,v in WIFI_DICT.items():
            if k == self.swarmer_id:
                continue
            c = Client()
            thread_args = [c, v['address'], v['port'], v['shared_q_index']]
            t = Thread(target=self.handle_outgoing_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.client_threads.append(t)

    def service_incoming_conns(self):
        print("Establishing incoming connections")
        for k,v in WIFI_DICT.items():
            if k == self.swarmer_id:
                continue
            s = Server(v['address'], v['port'])
            thread_args = [s, v['shared_q_index']]
            t = Thread(target=self.handle_incoming_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.server_threads.append(t)

    def handle_incoming_conn(self, server, idx):
        server.connect(True)
        while True:
            msg = server.recv() # set message size here
            self.server_lock.acquire()
            self.incoming_messages[idx].append(msg)
            self.server_lock.release()
            time.sleep(0.02)

    def handle_outgoing_conn(self, client, addr, port, idx):
        client.connect(addr, port, True)
        while True:
            msg = None
            self.client_lock.acquire()
            if len(self.outgoing_messages[idx]) > 0:
                msg = self.outgoing_messages.pop(0)
            self.client_lock.release()
            if msg:
                client.send(msg)
            time.sleep(0.02)

    def service_repl(self):
        while True:
            commands = sys.stdin.readline().split()
            if len(commands) > 0:
                command = commands[0]
                if command == HELP:
                    print(f"exit: {EXIT}")
                elif command == STATE:
                    print(self.state)
                elif command == EXIT:
                    print("Goodbye!")
                    return
                else:
                    continue
            else:
                print("Unsupported command. For list of supported commands type 'h'")

