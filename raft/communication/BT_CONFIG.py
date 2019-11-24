BT_DICT = {
    "S1": {
        "ADDR": "B8:27:EB:19:6A:75",
        "PORT": 3,
        "SHARED_Q_INDEX": 0
    },
    "S2": {
        "ADDR": "B8:27:EB:6A:D3:2D",
        "PORT": 4
        "SHARED_Q_INDEX": 1
    },
    "S3": {
        "ADDR": "B8:27:EB:0D:A8:B9",
        "PORT": 5
        "SHARED_Q_INDEX": 2
    }
}

SWARMER_ADDR_DICT = {
    "B8:27:EB:19:6A:75": "S1",
    "B8:27:EB:6A:D3:2D": "S2",
    "B8:27:EB:0D:A8:B9": "S3"
}

ALL_ADDRESSES = list(SWARMER_ADDR_DICT.keys())