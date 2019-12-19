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
* [\*] Write Usage Section
* [\*] Write Hardware Section
* [\*] Write Software Section
* [AS] Update website with progress

## Usage

1. Install `Python 3`

Run ./scripts/main_script.sh to kick off bash scripts on each pi.

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
#### Drivers
### Communication
#### Bluetooth Communication
### Raft
#### Leader
#### Candidate
#### Follower
### OpenCV
### Entry Scripts

## Misc
[check out our website](https://swarmyswarmers.github.io)
