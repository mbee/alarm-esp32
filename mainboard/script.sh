#!/usr/bin/env sh
while true; do for a in $(cat test.txt); do mosquitto_pub -h $MQTT_HOST -u $MQTT_USER -P $MQTT_PASSWORD -t alarm_command -m "{\"command\":\"display\", \"msg\":\"$a\"}"; sleep 0.2; done; done

