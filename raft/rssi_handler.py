import pickle
from sys import exit

from communication.rssi import BT_RSSI
from communication.BT_CONFIG import S_IDS

# WARNING: This file assumes that a valid 'rssi_ranges.pickle' file exists in the same directory

RANGE_FILE = 'rssi_ranges.pickle'
SAMPLE_SIZE = 20


class RssiHandler:
    def __init__(self, my_swarmer_id):
        self.rssi_range_dict = {}
        self.bt_rssi = BT_RSSI()
        self.rssi_reading_dict = {}
        self.my_id = my_swarmer_id

        for s_id in S_IDS:
            if s_id == my_swarmer_id:
                continue
            self.bt_rssi.connect(s_id)

        try:
            with open(RANGE_FILE, 'rb') as f:
                self.rssi_range_dict = pickle.load(f)
        except Exception as e:
            print(f"{e}")
            print(f"Error while init RssiHandler, does {RANGE_FILE} exist in the same directory?")
            exit(1)

    def am_i_close(self):
        for s_id in S_IDS:
            if s_id == self.my_id:
                continue
            self.rssi_reading_dict[s_id] = []
            for _ in range(SAMPLE_SIZE):
                self.rssi_reading_dict[s_id].append(self.bt_rssi.request_rssi(s_id))
            reading_avg = sum(self.rssi_reading_dict[s_id]) / len(self.rssi_reading_dict[s_id])
            close_range_avg = sum(self.rssi_range_dict[s_id][0]) / len(self.rssi_range_dict[s_id][0])
            far_range_avg = sum(self.rssi_range_dict[s_id][1]) / len(self.rssi_range_dict[s_id][1])
            comp_close = abs(reading_avg - close_range_avg)
            comp_far = abs(reading_avg - far_range_avg)
            if comp_close >= comp_far:
                return True
        return False


if __name__ == '__main__':
    from communication.SWARMER_ID import SWARMER_ID
    from time import sleep

    r = RssiHandler(SWARMER_ID)
    for _ in range(5):
        sleep(10)
        print(r.am_i_close())
