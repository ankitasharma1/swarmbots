WIFI_DICT = {
    'S1': {
        'ADDR': 'cslab3a',
        'PORT': 5000,
        'SHARED_Q_INDEX': 0
    },
    'S2': {
        'ADDR': 'cslab6a',
        'PORT': 6000,
        'SHARED_Q_INDEX': 1
    },
    'S3': {
        'ADDR': 'cleveland',
        'PORT': 7000,
        'SHARED_Q_INDEX': 2
    }
}

SWARMER_ADDR_DICT = {
    "cslab3a": "S1",
    "cslab6a": "S2",
    "cleveland": "S3"
}

ALL_ADDRESSES = list(SWARMER_ADDR_DICT.keys())