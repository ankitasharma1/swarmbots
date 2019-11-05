# TODO
import bluetooth
import sys

addr = 'D8:27:EB:6A:D3:2D'

print("Searching for %s" % addr)

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = bluetooth.find_service(uuid=uuid, address=addr)

if len(service_matches) == 0:
    print("couldn't find %s service" % addr)
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s" % (name, host))

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

print("connected.")

while True:
    try:
        data = input()
        if len(data) == 0: break
        sock.send(data)
    except KeyboardInterrupt:
        print("goodbye")
        sock.close()

