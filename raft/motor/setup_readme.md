# Required Libraries and Configuration
1. sudo pip3 install adafruit-circuitpython-motorkit
2. enable i2c interface in raspi-config

## Controller Only
3. sudo pip3 install keyboard

# Motor Connection

## Car Schematic

### Motor Location
                      ==============
            ------------------------
           *          M1            *
          *                          *
          * 0                        *  FRONT
          *                          *
           *          M2            *
            ------------------------
                      ==============

### Wiring to the RaspberryPi DC Motor HAT

    ----------------------------------------
    |                                      |
    |                                      |
    | DC+ Stepper                          |
    | Motor HAT                            |
    |                                      |
    |                                      |
    |   M1    GND    M2            5-12V   |
    | +    +   +   +    +          +   +   |
    ----------------------------------------
     M1B  M1R  .  M2R  M2B         BR  BB

#### Key
* '+': wire input that can be tightened with a philips screw-driver
* 'M1': Motor1 hub on the RPi DC Motor HAT board
* 'GND': Grounding hub on the RPi DC Motor HAT board
* 'M2': Motor2 hub on the RPi DC Motor HAT board
* '5-12V': Power hub on the RPi DC Motor HAT board
* 'M1B': black colored wire coming from Motor1 
* 'M1R': red colored wire coming from Motor1 
* '.': empty
* 'M2B': black colored wire coming from Motor2
* 'M2R': red colored wire coming from Motor2
* 'BR': red colored wire coming from the motor battery
* 'BB': black colored wire coming from the motor battery
