#!/usr/bin/env python3

from machine import UART
from umqtt.simple import MQTTClient
from log import log
from keypad import Keypad
from pins import Pins
from config import MQTT_HOST, MQTT_USER, MQTT_PASSWORD, PIN
import ujson


class Events(object):
    def __init__(self, keypad, pins):
        self.keypad = keypad
        self.keypad.listener = self
        self.pins = pins
        self.pins.listener = self

    def keyPressed(self, key):
        pass

    def keyReleased(self, key):
        pass

    def keyOnHold(self, key):
        pass

    def caseOpen(self, key):
        pass

    def pinStateChanged(self, key, value):
        pass


class Alarm(Events):
    def __init__(self, keypad, pins, mqtt):
        super().__init__(keypad, pins)
        self.state = "0"
        self.mqtt = mqtt
        self.pin = ""
        self.attempt = 0
        self.quit = False
        self.active = True
        log("Alarm init")
        self.sendStatus()
        self.mqtt.set_callback(self.mqtt_callback)
        self.mqtt.subscribe("alarm_command")
        self.setDisplay()

    def sendStatus(self):
        self.mqtt.publish("alarm", ujson.dumps({'active': self.active}))

    def setDisplay(self):
        firstLine = "Welcome!"
        if self.attempt == 0:
            firstLine += "        "
        else:
            firstLine = firstLine + "     " + \
                chr(ord("0") + self.attempt) + "/3"
        secondLine = "PIN"
        if len(self.pin) > 0:
            secondLine += ": " + self.pin
        else:
            if self.active == True:
                secondLine += " to disable."
            else:
                secondLine += " to enable."
        self.keypad.setDisplay(firstLine + secondLine)

    def keyPressed(self, key):
        if self.state in ["0", "PIN"] and (key >= "0" and key <= "9"):
            self.state = "PIN"
            self.pin += key
        elif self.state in ["PIN"] and (key == "X"):
            self.pin = ""
            self.state = "0"
        elif self.state in ["PIN"] and (key == "E") and self.pin == PIN:
            self.pin = ""
            self.active = not self.active
            self.attempt = 0
            self.state = "0"
            self.sendStatus()
        elif self.state in ["PIN"] and (key == "E") and self.pin != PIN:
            self.attempt += 1
            self.state = "0"
            self.pin = ""
        self.setDisplay()

    def keyReleased(self, key):
        if key == "X":
            self.quit = True
        pass

    def keyOnHold(self, key):
        pass

    def caseOpen(self, key):
        pass

    def mqtt_callback(self, topic, msg):
        data = ujson.loads(msg)
        if 'command' in data and data['command'] == "display":
            self.keypad.setDisplay(data['msg'])

    def pinStateChanged(self, key, value):
        self.mqtt.publish("alarm/pin/"+key+"/state", ujson.dumps(value))

    def loop(self):
        while not self.quit:
            self.keypad.loop()
            self.mqtt.check_msg()
            self.pins.loop()


uart = UART(2, 9600, bits=8, parity=None, stop=1)
uart.init(9600, bits=8, parity=None, stop=1)


def loop():
    mqtt = MQTTClient("umqtt_alarm", MQTT_HOST, port=1883,
                      user=MQTT_USER, password=MQTT_PASSWORD)
    mqtt.connect()
    kp = Keypad(uart)
    pins = Pins([{"label": "hall", "value": 4},
                 {"label": "stairs", "value": 5},
                 {"label": "cellar", "value": 18},
                 {"label": "unassigned19", "value": 19}],
                [{"label": "unassigned21", "value": 21},
                 {"label": "unassigned22", "value": 22},
                 {"label": "unassigned23", "value": 23}])
    alarm = Alarm(kp, pins, mqtt)
    alarm.loop()
