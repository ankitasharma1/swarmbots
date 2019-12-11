from time import sleep
import pickle

from communication.rssi import BT_RSSI
from communication.SWARMER_ID import SWARMER_ID
from communication.BT_CONFIG import S_IDS
from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE

SAMPLE_SIZE = 1000
RESULT_FILE = 'rssi_ranges.pickle'


class RssiCalibrator:
    def __init__(self):
        self.rssi_dicts = {}
        self.motor = MotorDriver(THROTTLE / 1.3)
        self.rssi = BT_RSSI()

    def calibrate(self):
        for s_id in S_IDS:
            if s_id == SWARMER_ID:
                continue
            self.rssi.connect(s_id)
            print(f"connected to {s_id}")
            self.rssi_dicts[s_id] = {0: None, 1: None, 2: None}
        for i in range(3):
            if i != 0:
                self.motor.forward()
                sleep(1.5)
                self.motor.stop()
            for s_id in S_IDS:
                if s_id == SWARMER_ID:
                    continue
                rssi_samples = []
                for _ in range(SAMPLE_SIZE):
                    rssi_samples.append(self.rssi.request_rssi(s_id))
                self.rssi_dicts[s_id][i] = rssi_samples
        for i in range(3):
            if i != 0:
                self.motor.backward()
                sleep(3)
                self.motor.stop()
            for s_id in S_IDS:
                if s_id == SWARMER_ID:
                    continue
                rssi_samples = []
                for _ in range(SAMPLE_SIZE):
                    rssi_samples.append(self.rssi.request_rssi(s_id))
                self.rssi_dicts[s_id][i] += rssi_samples

    def print_rssi(self):
        print(self.rssi_dicts)

    def store_rssi(self):
        with open(RESULT_FILE, 'wb') as f:
            pickle.dump(self.rssi_dicts, f)

    def print_avgs(self):
        for s_id in S_IDS:
            if s_id == SWARMER_ID:
                continue
            close_avg = sum(self.rssi_dicts[s_id][0]) / len(self.rssi_dicts[s_id][0])
            mid_avg = sum(self.rssi_dicts[s_id][1]) / len(self.rssi_dicts[s_id][1])
            far_avg = sum(self.rssi_dicts[s_id][2]) / len(self.rssi_dicts[s_id][2])

            print(f"{s_id} close avg dbm: {close_avg}")
            print(f"{s_id} mid avg dbm: {mid_avg}")
            print(f"{s_id} far avg dbm: {far_avg}")

    def sanity_check(self):
        with open(RESULT_FILE, 'rb') as f:
            temp = pickle.load(f)
        print(f"Are pickle and live object equal: {temp == self.rssi_dicts}")


if __name__ == '__main__':
    r = RssiCalibrator()
    r.calibrate()
    # r.print_rssi()
    r.store_rssi()
    r.print_avgs()
    r.sanity_check()
