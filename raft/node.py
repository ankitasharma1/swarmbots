import sys
import threading
from threading import Thread
import socket
import time

from communication.server import Server
from communication.client import Client
from communication.bt_server import BT_Server
from communication.bt_client import BT_Client

from WIFI_CONFIG import WIFI_DICT
from communication.BT_CONFIG import BT_DICT, ALL_ADDRESSES, SWARMER_ADDR_DICT

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
    def __init__(self, swarmer_id, wifi=False, debug=False):
        print(f"Creating Node: {swarmer_id}")
        self.swarmer_id = swarmer_id
        self.state = JOIN
        self.debug = debug
        self.wifi = wifi
        if wifi:
            self.config_dict = WIFI_DICT
        else:
            self.config_dict = BT_DICT

        self.host = self.config_dict[swarmer_id]["ADDR"]
        self.port = self.config_dict[swarmer_id]["PORT"]

        if wifi:
            self.server = Server(self.host, self.port, swarmer_id, debug)
        else:
            self.server = BT_Server(self.host, self.port, swarmer_id, debug)

        self.client_count = 0

        # Message queues, needs locking in each server thread
        self.incoming_messages = [[] for _ in range(len(self.config_dict))]
        self.outgoing_messages = [[] for _ in range(len(self.config_dict))]

        # Basic synchronization is required to kep track of alive/closed sockets.
        self.server_thread = None
        self.client_threads = []
        self.server_lock = threading.Lock()
        self.client_lock = threading.Lock()


    def init(self):
        self.service_incoming_conns()
        self.service_outgoing_conns()

        while (not self.client_count < 2) or (not len(self.server.clients) < 2):
            sleep(0.05)
            print("Waiting for servers to connect ...")

        """
        Kick off REPL.
        """
        self.service_repl() 

    def send_to(self, client_id_list, msg):
        for c_id in client_id_list:
            if c_id == self.swarmer_id:
                continue
            shared_q_index = self.config_dict[c_id]['SHARED_Q_INDEX']
            self.client_lock.acquire()
            self.outgoing_messages[shared_q_index].append(msg)
            self.client_lock.release()

    def recv_from(self, server_id_list):
        for s_id in server_id_list:
            if s_id == self.swarmer_id:
                continue
            q_idx = self.config_dict[s_id]['SHARED_Q_INDEX']
            self.server_lock.acquire()
            msg = self.incoming_messages[q_idx].pop(0)
            self.server_lock.release()
            # print(f"Received msg from {s_id}: {msg}")
            return msg

    def service_outgoing_conns(self):
        print("Establishing outgoing connections")
        for k,v in self.config_dict.items():
            if k == self.swarmer_id:
                continue
            if self.wifi:
                c = Client(k, self.debug)
            else:
                c = BT_Client(k, self.debug)
            thread_args = [c, v['ADDR'], v['PORT'], v['SHARED_Q_INDEX']]
            t = Thread(target=self.handle_outgoing_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.client_threads.append(t)

    def service_incoming_conns(self):
        print("Establishing incoming connections")
        for k,v in self.config_dict.items():
            if k == self.swarmer_id:
                continue
            thread_args = [self.server]
            t = Thread(target=self.handle_incoming_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.server_thread = t

    def handle_incoming_conn(self, server):
        while True:
            for addr in ALL_ADDRESSES:
                msg = server.recv(addr) # set message size here
                if msg:
                    s_id = SWARMER_ADDR_DICT[addr]
                    q_idx = BT_DICT[s_id]["SHARED_Q_INDEX"]
                    self.server_lock.acquire()
                    self.incoming_messages[q_idx].append(msg)
                    self.server_lock.release()

    def handle_outgoing_conn(self, client, addr, port, idx):
        client.connect(addr, port)
        self.client_count += 1
        while True:
            msg = None
            self.client_lock.acquire()
            if len(self.outgoing_messages[idx]) > 0:
                msg = self.outgoing_messages.pop(0)
            self.client_lock.release()
            if msg:
                client.send(msg)

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

