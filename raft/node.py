import sys
from threading import Thread, Lock
import time
import json

from states import do_raft

from communication.server import Server
from communication.client import Client
from communication.bt_server import BT_Server
from communication.bt_client import BT_Client

from communication.WIFI_CONFIG import WIFI_DICT, WIFI_ADDRESSES, WIFI_ADDR_DICT
from communication.BT_CONFIG import BT_DICT, BT_ADDRESSES, BT_ADDR_DICT
from communication.MSG_CONFIG import MSG_SIZE

from communication.message import deserialize

"""
REPL Commands
"""
EXIT = 'e'
HELP = 'h'
STATE = 's'
TERM = 't'


class Node:
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

        # Basic synchronization is required to keep track of alive/closed sockets.
        self.server_thread = None
        self.client_threads = []
        self.server_lock = Lock()
        self.client_lock = Lock()

        # Raft info
        self.seed = self.config_dict[swarmer_id]["SEED"]
        self.state = 'join'
        self.old_state = ""        
        self.term = 0
        self.voted_for = None

        self.other_s_ids = list(BT_DICT.keys())
        self.other_s_ids.remove(swarmer_id)

    def init(self):
        self.service_incoming_conns()
        self.service_outgoing_conns()

        while (self.client_count < 2) or (len(self.server.clients) < 2):
            time.sleep(0.05)

        t = Thread(target=self.start_raft)
        t.setDaemon(True)
        t.start()

        self.service_repl()

    def start_raft(self):
        do_raft(self)

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
                # print(f"Received msg from {server_id}: {msg}")
            self.server_lock.release()
            return msg

    def service_outgoing_conns(self):
        print("Establishing outgoing connections")
        print(f"Debug status: {self.debug}")
        for k, v in self.config_dict.items():
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
        for k, v in self.config_dict.items():
            if k == self.swarmer_id:
                continue
            thread_args = [self.server]
            t = Thread(target=self.handle_incoming_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.server_thread = t

    def handle_incoming_conn(self, server):
        # Keep track of byte stream for each socket.
        prev_msg = dict()
        for addr in self.all_addresses:
            prev_msg.update({addr: ""})
        
        while True:
            for addr in self.all_addresses:
                if addr == self.config_dict[self.swarmer_id]["ADDR"]:
                    continue
                s_id = self.addr_dict[addr]
                msg = server.recv(addr)  # set message size here
                print(f"Received message from {s_id}")
                # x = msg  # debugging purposes
                print(f"Sleeping now")
                time.sleep(0.75)
                if msg:
                    print(f"========= {msg} ==========")
                    q_idx = self.config_dict[s_id]["SHARED_Q_INDEX"]
                    msg_dict = deserialize(msg)
                    if msg_dict:
                        self.server_lock.acquire()
                        self.incoming_messages[q_idx].append(msg)
                        self.server_lock.release()

                # if msg:
                #     # Check if all of the bytes have arrived.
                #     if len(msg) != MSG_SIZE:
                #         # Check if a prev message exists.
                #         prev = prev_msg.get(addr)
                #         if len(prev) > 0:
                #             msg = prev + msg
                #             # If all of the bytes have been received, we are done.
                #             if len(msg) == MSG_SIZE:
                #                 prev_msg.update({addr: ""})
                #             # Continue what we are doing until all bytes are received.
                #             else:
                #                 prev_msg.update({addr: msg})
                #         # We are waiting for subsequent bytes.
                #         else:
                #             prev_msg.update({addr: msg})
    
                #     # Only if the message is 1024 bytes add it to the queue.
                #     if len(msg) == MSG_SIZE:
                #         s_id = self.addr_dict[addr]
                #         q_idx = self.config_dict[s_id]["SHARED_Q_INDEX"]
                #         self.server_lock.acquire()
                #         # This is a bandaid. Idk why we are receiving malformed messages...
                #         if not msg.startswith("{"):
                #             msg = msg.split("{")[1]
                #             msg = "{" + msg
                #         if not msg.endswith("}"):
                #             msg = msg + '"' + "}"
                #         # Sanity check/for debugging purposes since this will happen down the line.
                #         try:
                #           json.loads(msg)
                #           self.incoming_messages[q_idx].append(msg)
                #         except Exception as e:
                #             print("=============================")
                #             print(e)
                #             print(f"{x}")
                #             print("===============")
                #             print(f"{msg}")
                #             print("=============================")
                #             # The message is essentially dropped if it can't be properly parsed.
                #         self.server_lock.release()

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
