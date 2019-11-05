# README for setting up bluetooth stuff on new swarmer
1. sudo apt-get update
2. turn on I2C and other interfaces: preferences > Raspberry Pi Configuration >
   Interfaces
3. sudo reboot now
4. sudo apt-get install libbluetooth0dev
5. sudo pip3 install pybluez
6. sudo hciconfig hci0 piscan
7. modify /etc/bluetooth/main.conf
  * Class = 0x400100
  * DiscoverableTimeout = 0
  * FastConnectable = True
8. modify /etc/systemd/system/dbus-org.bluez.service adding -C for under SERVICE
   after bluetoothd for ExecStart
9. sudo sdptool add SP
10. follow guide here: stackoverflow.com/questions/34599703
  * remember to add the chmod line in ExecStartPost
11. sudo reboot now
