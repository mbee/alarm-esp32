# This file is executed on every boot (including wake-boot from deepsleep)
from alarm import loop
import network
import ubinascii
import machine
from config import SSID, PASSWORD

# nothing to be changed after this point
client_id = ubinascii.hexlify(machine.unique_id())

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())

loop()
