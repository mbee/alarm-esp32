# alarm-esp32

Interfacing esp32 to an old honeywell alarm with keypad.

## current status

Quick & dirty proof of concept to interface an ESP32 to an old (~1990) Honeywell alarm (a.k.a.ELKRON in France). The code runs on an ESP32 thanks to micropython. It can:

- dialog with a Honeywell Galaxy keypad CP038
- handle a pin to activate or disable the alarm
- get motion sensor status
- send mqtt status for alarm and sensors
- receive mqtt to display a message on the keypad

## Prerequesites

- a Honeywell alarm
- an ESP32 (works also on ESP8266, with different pins, check on esp8266 directory)
- a CP038 keypad
- RS485 <=> TTL converter, such as XY-017 <https://www.amazon.fr/gp/product/B07RKY1G71>. This one swithes automatically the DE/RE level on the MAX485, which is quite convenient, as we can deal with RX/TX directly instead on ESP32 uart 2.

## TODO

- handle a su2 external keypad to disable/enable the alarm from outside <https://www.automatisme-online.fr/su2-clavier-numerique-acie-acie-456.html>
- hide the pin code
- refactor keypad.py as it is too C-ish
- schema

## References

- <http://datashed.science/projects/galaxy/protocol/>
- <https://richard.burtons.org/2019/03/09/honeywell-galaxy-g2-rs485-bus/>
- <https://richard.burtons.org/2019/03/09/honeywell-galaxy-keypad-cp038-rs485-protocol/>
- <https://github.com/revk/SolarSystem>

