BT_DICT = {
    "S1": {
        "ADDR": "B8:27:EB:19:6A:75",
        "S2_PORT": 3,
        "S3_PORT": 4,
        "SHARED_Q_INDEX": 0,
        "SEED": 10
    },
    "S2": {
        "ADDR": "B8:27:EB:6A:D3:2D",
        "S1_PORT": 5,
        "S3_PORT": 6,
        "SHARED_Q_INDEX": 1,
        "SEED": 15
    },
    "S3": {
        "ADDR": "B8:27:EB:0D:A8:B9",
        "S1_PORT": 7,
        "S2_PORT": 8,
        "SHARED_Q_INDEX": 2,
        "SEED": 20
    }
}

BT_CONTROLLER_DICT = {
    "CONTROLLER": {
        "ADDR": "B8:27:EB:AE:E2:7D",
        "PORT": 12
    }
}

BT_ADDR_DICT = {
    "B8:27:EB:19:6A:75": "S1",
    "B8:27:EB:6A:D3:2D": "S2",
    "B8:27:EB:0D:A8:B9": "S3"
}

BT_ADDRESSES = list(BT_ADDR_DICT.keys())
S_IDS = list(BT_DICT.keys())
