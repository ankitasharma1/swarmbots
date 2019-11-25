import sys
import threading
from threading import Thread
import socket
import time

import states

from communication.server import Server
from communication.client import Client
from communication.bt_server import BT_Server
from communication.bt_client import BT_Client

from WIFI_CONFIG import WIFI_DICT, WIFI_ADDRESSES, WIFI_ADDR_DICT
from communication.BT_CONFIG import BT_DICT, BT_ADDRESSES, BT_ADDR_DICT

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
TERM = 't'

"""
States
"""
JOIN = 'join'

class Node():
    def __init__(self, swarmer_id, wifi=False, debug=False):
        print(f"Creating Node: {swarmer_id}")
        self.swarmer_id = swarmer_id
        self.debug = debug
        self.wifi = wifi
        if wifi:
            self.config_dict = WIFI_DICT
            self.all_addresses = WIFI_ADDRESSES
            self.addr_dict = WIFI_ADDR_DICT
        else:
            self.config_dict = BT_DICT
            self.all_addresses = BT_ADDRESSES
            self.addr_dict = BT_ADDR_DICT

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

        # Raft info
        self.state = JOIN        
        self.term = 0

        self.other_s_ids = list(BT_DICT.keys())
        self.other_s_ids.remove(swarmer_id)

    def init(self):
        self.service_incoming_conns()
        self.service_outgoing_conns()

        while (self.client_count < 2) or (len(self.server.clients) < 2):
            time.sleep(0.05)
            #print("Waiting for servers to connect ...")

        t = Thread(target=self.start_raft)
        t.setDaemon(True)
        t.start()

        """
        Kick off REPL.
        """
        self.service_repl() 

    def start_raft(self):
        states.do_raft(self)

    def send_to(self, client_id_list, msg):
        for c_id in client_id_list:
            if c_id == self.swarmer_id:
                continue
            shared_q_index = self.config_dict[c_id]['SHARED_Q_INDEX']
            self.client_lock.acquire()
            self.outgoing_messages[shared_q_index].append(msg)
            self.client_lock.release()

    def recv_from(self, server_id):
        if server_id != self.swarmer_id:        
            q_idx = self.config_dict[server_id]['SHARED_Q_INDEX']
            msg = None
            self.server_lock.acquire()
            if len(self.incoming_messages[q_idx]) > 0:
                msg = self.incoming_messages[q_idx].pop(0)
                #print(f"Received msg from {server_id}: {msg}")
            self.server_lock.release()
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
            for addr in self.all_addresses:
                msg = server.recv(addr) # set message size here
                if msg:
                    s_id = self.addr_dict[addr]
                    q_idx = self.config_dict[s_id]["SHARED_Q_INDEX"]
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
                msg = self.outgoing_messages[idx].pop(0)
            self.client_lock.release()
            if msg:
                client.send(msg)

    def service_repl(self):
        while True:
            commands = sys.stdin.readline().split()
            if len(commands) > 0:
                command = commands[0]
                if command == HELP:
                    print(f"Supports {EXIT}, {HELP}, {STATE}, {TERM}")
                    continue
                elif command == STATE:
                    print(self.state)
                elif command == TERM:
                    print(self.term)
                elif command == EXIT:
                    self.server.clean_up()
                    print("Goodbye!")
                    return
                else:
                    print(f"Supports {EXIT}, {HELP}, {STATE}, {TERM}")
                    continue
            else:
                print("Unsupported command. For list of supported commands type 'h'")
