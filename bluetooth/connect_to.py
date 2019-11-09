import bluetooth as BT
import sys
from time import sleep


class ConnectToAgent():
    def __init__(self, to_addr, uuid):
        self.connected = False
        self.to_addr = to_addr
        self.uuid = uuid
        self.bt_sock = None

    def connect(self, try_again=False):
        service_matches = BT.find_service(uuid=self.uuid, address=self.to_addr)
        if len(service_matches) == 0:
            print(f"WARNING: Couldn't find service from {self.to_addr}")
            if try_again:
                print("\tTrying again in 5 seconds ...")
                time.sleep(5)
                self.connect()
        else:
            # there should only be a single match
            port = service_matches[0]["port"]
            host = service_matches[0]["host"]
            print(f"Service for {self.to_addr} found, connecting to {host} on port {port}")
            bt_sock = BT.BluetoothSocket(BT.RFCOMM)
            bt_sock.connect((host, port))
            print(f"Connected to {host} on port {port}")
            self.bt_sock = bt_sock
            self.connected = True

    def send(self, msg):
        if self.connected:
            self.bt_sock.send(msg)
            return True
        else:
            return False

    def clean_up(self):
        self.bt_sock.close()
        self.connected = False

if __name__ == "__main__":
    # testing
    from SWARMER_BT_INFO import UUID
    
    t = ConnectToAgent('B8:27:EB:19:6A:75', UUID)
    t.connect()
    t.send("Hello")
    sleep(0.1)
    t.send("Again")
    sleep(0.5)
    t.send("YO!")

    t.clean_up()
