from machine import Pin
import ujson

inputs = [0, 2, 4, 5]
outputs = [12, 13, 14, 15, 16]
pinsIn = [Pin(i, Pin.IN, Pin.PULL_UP) for i in inputs]
pinsOut = [Pin(i, Pin.OUT, value=0) for i in outputs]
inputsSavedState = [i.value() for i in pinsIn]


def loop(mqtt):
    for i in range(len(inputs)):
        newValue = pinsIn[i].value()
        if newValue != inputsSavedState[i]:
            if i == 3:
                return False
            mqtt.publish(
                "alarm/pin/"+str(inputs[i])+"/state", ujson.dumps({"value": newValue}))
            inputsSavedState[i] = newValue
    return True
