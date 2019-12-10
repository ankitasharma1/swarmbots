import bluetooth
import bluetooth._bluetooth as bt
import struct
import array
import fcntl

from .BT_CONFIG import BT_DICT


class BT_RSSI(object):
    def __init__(self):
        self.hci_sock = bt.hci_open_dev()
        self.hci_fd = self.hci_sock.fileno()

        self.bt_socks = {}

    def prep_cmd_pkt(self, swarmer_id):
        """Prepare the command packet for requesting RSSI."""
        addr = BT_DICT[swarmer_id]["ADDR"]
        reqstr = struct.pack(b'6sB17s', 
                             bt.str2ba(addr), 
                             bt.ACL_LINK, 
                             b'\0' * 17)
        request = array.array('b', reqstr)
        handle = fcntl.ioctl(self.hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack(b'8xH14x', request.tobytes())[0]
        return struct.pack('H', handle)

    def connect(self, swarmer_id):
        """Connect to the Bluetooth device."""
        bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        bt_sock.settimeout(10)
        addr = BT_DICT[swarmer_id]["ADDR"]
        bt_sock.connect_ex((addr, 1)) # connect PSM 1 - Service Discovery
        self.bt_socks[swarmer_id] = bt_sock
        return True
   
    def remove_sock(self, swarmer_id):
        self.bt_socks.pop(swarmer_id, None)

    def clean_up(self):
        """Close the bluetooth socket."""
        self.hci_sock.close()

    def request_rssi(self, swarmer_id):
        """Request the current RSSI value.
        @return: The RSSI value or None if the device connection fails
                 (i.e. the device is not in range).
        """
        try:
            # If socket is closed, return nothing
            if swarmer_id not in self.bt_socks:
                self.connect(swarmer_id)
            # Command packet prepared each iteration to allow disconnect to trigger IOError
            cmd_pkt = self.prep_cmd_pkt(swarmer_id)
            # Send command to request RSSI
            rssi = bt.hci_send_req(self.hci_sock, 
                                   bt.OGF_STATUS_PARAM,
                                   bt.OCF_READ_RSSI, 
                                   bt.EVT_CMD_COMPLETE, 
                                   4, 
                                   cmd_pkt)
            rssi = struct.unpack('b', rssi[3].to_bytes(1, 'big'))
            return rssi[0]
        except IOError:
            # Socket recreated to allow device to successfully reconnect
            self.remove_sock(swarmer_id)
            self.connect(swarmer_id)
            return self.request_rssi(swarmer_id)


if __name__ == '__main__':
    # s_id = 'S1'
    # s_id = 'S2'
    s_id = 'S3'
    n_samples = 10
    rssi_samples = []
    
    r = BT_RSSI()

    r.connect(s_id)

    if n_samples == 1:
        print(r.request_rssi(s_id))
    else:
        for _ in range(n_samples):
            rssi_samples.append(r.request_rssi(s_id))
        print(rssi_samples)
    
    r.remove_sock(s_id)
    r.clean_up()
