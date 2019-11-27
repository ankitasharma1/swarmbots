WIFI_DICT = {
    'S1': {
        'ADDR': '10.116.72.111', #cslab3a
        'PORT': 5000,
        'SEED': 10,
        'SHARED_Q_INDEX': 0
    },
    'S2': {
        'ADDR': '10.116.72.55', #cslab6a
        'PORT': 6000,
        'SEED': 15,        
        'SHARED_Q_INDEX': 1
    },
    'S3': {
        'ADDR': '10.116.74.25', #cleveland
        'PORT': 7000,
        'SEED': 20,        
        'SHARED_Q_INDEX': 2
    }
}

WIFI_ADDR_DICT = {
    "10.116.72.111": "S1",
    "10.116.72.55": "S2",
    "10.116.74.25": "S3"
}

WIFI_ADDRESSES = list(WIFI_ADDR_DICT.keys())
