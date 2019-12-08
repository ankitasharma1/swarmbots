import sys
from threading import Thread, Lock
import time

from states import do_raft

from communication.server import Server
from communication.client import Client
from communication.bt_server import BT_Server
from communication.bt_client import BT_Client

from communication.WIFI_CONFIG import WIFI_DICT, WIFI_ADDRESSES, WIFI_ADDR_DICT
from communication.BT_CONFIG import BT_DICT, BT_ADDRESSES, BT_ADDR_DICT, S_IDS

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

        self.client_count = 0

        # Message queues, needs locking in each server thread
        self.incoming_msg_dict = {s_id: [] for s_id in S_IDS}
        self.outgoing_msg_dict = {s_id: [] for s_id in S_IDS}
        # self.incoming_messages = [[] for _ in range(len(self.config_dict))]
        # self.outgoing_messages = [[] for _ in range(len(self.config_dict))]

        # Basic synchronization is required to keep track of alive/closed sockets.
        self.server_threads = []
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

        print("init before cluster connect guard")

        while (self.client_count < 2) or (len(self.server.clients) < 2):
            time.sleep(0.2)

        print("init after cluster connect guard")

        t = Thread(target=self.start_raft)
        t.setDaemon(True)
        t.start()

        print("raft started, starting REPL")

        self.service_repl()

    def start_raft(self):
        print("Starting Raft")
        do_raft(self)

    def send_to(self, client_id_list, msg):
        for c_id in client_id_list:
            if c_id == self.swarmer_id:
                continue
            self.client_lock.acquire()
            print(f">>> Qeueing {msg} to send to {c_id}")
            self.outgoing_msg_dict[c_id].append(msg)
            self.client_lock.release()

    def recv_from(self, server_id):
        if server_id != self.swarmer_id:        
            msg = None
            self.server_lock.acquire()
            if len(self.incoming_msg_dict[server_id]) > 0:
                msg = self.incoming_msg_dict[server_id].pop(0)
            self.server_lock.release()
            return msg

    def service_outgoing_conns(self):
        print("Establishing outgoing connections")
        for s_id in S_IDS:
            if s_id == self.swarmer_id:
                continue
            c = BT_Client(self.swarmer_id, self.debug)
            host = self.config_dict[self.swarmer_id]["ADDR"]
            port = self.config_dict[s_id][f"#{self.swarmer_id}_PORT"]
            thread_args = [c, host, port, s_id]
            t = Thread(target=self.handle_outgoing_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.client_threads.append(t)

    def service_incoming_conns(self):
        print("Establishing incoming connections")
        for s_id in S_IDS:
            if s_id == self.swarmer_id:
                continue
            host = self.config_dict[self.swarmer_id]["ADDR"]
            port = self.config_dict[self.swarmer_id][f"{s_id}_PORT"]
            s = BT_Server(host, port, self.swarmer_id, self.debug)
            thread_args = [s, s_id]
            t = Thread(target=self.handle_incoming_conn, args=thread_args)
            t.setDaemon(True)
            t.start()
            self.server_threads.append(t)

    def handle_incoming_conn(self, server, s_id):
        addr = self.config_dict[s_id]["ADDR"]
        while True:
            msg = server.recv(addr)  # set message size here
            print(f"Received message {msg} from {s_id}")
            if msg:
                print(f"========= {msg} ==========")
                msg_dict = deserialize(msg)
                if msg_dict:
                    self.server_lock.acquire()
                    self.incoming_msg_dict[s_id].append(msg)
                    self.server_lock.release()
            print(f"{s_id} Server Recv sleeping now")
            time.sleep(1)

    def handle_outgoing_conn(self, client, addr, port, s_id):
        client.connect(addr, port)
        print(f"Connected to {s_id}:{addr}:{port}")
        self.client_count = self.client_count + 1
        print(f"Client count: {self.client_count}")
        while True:
            msg = None
            self.client_lock.acquire()
            if len(self.outgoing_msg_dict[s_id]) > 0:
                msg = self.outgoing_msg_dict[s_id].pop(0)
                print(f">>> Sending message {msg} to {s_id}")
            self.client_lock.release()
            if msg:
                client.send(msg)
            print(f"{s_id} Client Send sleeping now")
            time.sleep(1)

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
