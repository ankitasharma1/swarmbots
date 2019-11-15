import bluetooth as BT

from SWARMER_ID import SWARMER_ID
from SWARMER_BT_INFO import SWARMER_ADDR_DICT


class BT_Server():
    def __init__(self, uuid, msg_size):
        self.connected = False
        self.from_addr = None
        self.client_sock = None
        self.client_info = None
        self.uuid = uuid
        self.server_sock = BT.BluetoothSocket(BT.RFCOMM)
        self.name = SWARMER_ID + " Receiver"
        self.msg_size = msg_size

        # init bt socket
        self.server_sock.bind(("", BT.PORT_ANY))
        self.server_sock.listen(1)

        self.port = self.server_sock.getsockname()[1]

    def advertise(self):
        BT.advertise_service(self.server_sock,
                             self.name,
                             service_id=self.uuid,
                             service_classes=[
                                 self.uuid,
                                 BT.SERIAL_PORT_CLASS],
                             profiles=[BT.SERIAL_PORT_PROFILE])
        print(f"Waiting for connection on port {self.port} ...")
        self.client_sock, self.client_info = self.server_sock.accept()
        print(f"Connected to {self.client_info[0]} on port {self.client_info[1]}")
        self.connected = True

    def read(self):
        if self.connected:
            data = self.client_sock.recv(self.msg_size)
            return data
        else:
            return None

    def get_client_name(self):
        if self.connected:
            return SWARMER_ADDR_DICT[self.client_info[0]]

    def clean_up(self):
        try:
            self.client_sock.close()
        except:
            pass

        try:
            self.server_sock.close()
        except:
            pass

        self.connected = False

if __name__ == "__main__":
    # testing
    from SWARMER_BT_INFO import UUID

    msg_size = 10 # bytes

    try:
        t = RecvFromAgent(UUID, msg_size)
        t.advertise()
        while True:
            receivedData = t.read()
            if receivedData:
                print(receivedData)
                # break
    except:
        print("Connection dead, starting clean up")

    t.clean_up()
