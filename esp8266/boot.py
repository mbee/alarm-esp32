# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
# esp.osdebug(None)
#import uos, machine
# uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import network
import time
from testpin import loop
from time import sleep
from umqtt.simple import MQTTClient
from config import SSID, PASSWORD, MQTT_HOST, MQTT_USER, MQTT_PASSWORD

gc.collect()

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)
while not sta_if.isconnected():
    time.sleep(1)

print('network config:', sta_if.ifconfig())

mqtt = MQTTClient("umqtt_alarm", MQTT_HOST, port=1883,
                  user=MQTT_USER, password=MQTT_PASSWORD)
mqtt.connect()

while loop(mqtt):
    sleep(1)
