# swarmy swarmers

__TODO:__
* [JR] ~~Implement `follow` using corrected-RSSI (formerly named anti-collision)~~
* [JA] ~~Implement `follower_orient` using OpenCV~~
* [JR] ~~Implement `follower_drive`~~
* [JR] ~~Implement on-start-up scripts~~
* [JR + AS] ~~Implement `main.py` to tie everything together~~
* [AS] ~~Clean up `raft`, allowing it to be passed BT channels~~
* [JR] ~~Put together swarmer3~~
* [JA] ~~Figure out how to mount the camera to a robot~~
* [JR] ~~Put together controller hardware~~
* [AS] ~~Write start-up scripts for controller~~
* [\*] ~~Write Usage Section~~
* [\*] ~~Write Hardware Section~~
* [\*] Write Software Section
* [AS] ~~Update website with progress~~
* [JR] Test possible speed up by replacing BT and OpenCV threads with Processes

## Usage
1. Setup each Pi to accept SSH
2. Follow the `setup_readme.md` in each subfolder -- this involves installing libraries, writing configs, and setting environment variables
3. Run `./scripts/main_script.sh` from your main computer to kick off bash scripts on each Pi

## Hardware
### Car
#### Components
* RaspberryPi 3B
* Mini Round Robot Chassis Kit - 2WD with DC Motors
* Lithium Ion Cylindrical Battery - 3.7v 2200mAh
* USB Battery Pack for Raspberry Pi - 5000mAh - 5V @ 2.1A
* Brass M2.5 Standoffs for Pi HATs - Black Plated - Pack of 2
* Arducam 5 Megapixels 1080p Sensor OV5467 Mini Camera Video Module
* Adafruit DC & Stepper Motor HAT for Raspberry Pi - Mini Kit
* SanDisk 32GB Ultra MicroSDHC UHS-I Memory Card with Adapter
* Makerfocus TP4056 5V Micro USB 1A 18650 Lithium Battery Charging Board
* About 3 inches of spare wire
#### Instructions
1. Flash RaspbianOS on the SD card
2. Cut the white plastic cap off the Lithium Ion Cylindrical Battery
3. Strip roughly 0.5 inches of the wires coming from the battery
4. Solder the wires into the charging board
5. Solder the spare wire into the charging board
6. Put the camera ribbon cable through the Motor HAT and lock it into the ribbon cable input
7. Install the Motor HAT onto the Pi
8. Hook the wires from each motor into the Motor HAT followingt the `setup_readme.md` in the motor folder
9. Power the Pi using the USB Battery Pack
10. Power the Motor HAT using the Lithium Ion Cylindrical Battery leads from the Charging Board
11. Using card board and a ton of duct tape, position the camera above the bot

### Controller
* Raspberry Pi Zero W
* REIIE H9+ Backlit Wireless Mini Handheld Remote Keyboard with Touchpad
* Makerfocus TP4056 5V Micro USB 1A 18650 Lithium Battery Charging Board
* Lithium Ion Cylindrical Battery - 3.7v 2200mAh
* SanDisk 32GB Ultra MicroSDHC UHS-I Memory Card with Adapter

## Software
### Motor
The motor uses adafruit circuit-python's motor driver library. We implemented a wrapper around the libraries APIs to give the motors a failsafe and make modularized calls to move.

### Communication
#### Interbot Communication
Communication between bots is done over Bluetooth. Each bot is fully connected to the cluster excluding the controller. Only the controller and the current Leader bot have a Bluetooth connection. The `bt_server.py` and `bt_client.py` files contain code wrapping the pybluez bluetooth python library. The wrapper code adds debug-printing, uniform messaging, and self-healing features to both clients and servers.

#### RSSI
The bots use Bluetooth l2ping to collect RSSI (received signal strength indicator) between each bot in order to prevent collision. The `rssi.py` and `rssi_handler.py` are our implementations of an automated RSSI collector. They were made to take an arbitrary number of samples and save their metrics to a python pickle file to be used by other python processes. The `rssi_calibrator.py` calibrates the collector so that the samples are reliable. It calibrates by taking 5000 samples at 4 different points in the movement space then uses euclidian distance from the samples to quantify a custom _too-close_ area band for each bot. 

### Raft
Our bots run RAFT's election protocol found here [raft](https://raft.github.io/raft.pdf). All bots will start in the Follower state.

#### Leader
Each bot has successfully been elected leader it will stop running openCV and stop pinging for RSSI. It will then connect to the controller and start accept drive commands. It will also send heartbeat messages to all its followers.

#### Candidate
During the candidate state, the bot will stop motor functions, openCV, and RSSI pings. It will wait until its election is over to start driving again.

#### Follower
A bot in a follower state will start openCV to orient itself, RSSI pings to prevent collision and sense when the leader is out of range. 

### OpenCV
We put uniquely designed sticky notes on the back of each bot then trained a cascade model to recognize them. We also wrote code to wrap around the classification to give us the height, width, and relative position of the classification so that our bots could orient themselves towards a sticky note. The model is trained to recognize any of the sticky notes, including its own. This solves the problem of a follower eclipsing the leader from another follower. In the event of an eclipse, the eclipsed bot will simply form a caravan-like formation, following the follow in front of it.

### Entry Scripts
TODO

## Misc
[check out our website](https://swarmyswarmers.github.io)
