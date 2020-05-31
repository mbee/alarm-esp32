from machine import Pin


class Pins(object):
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.pinsIn = [Pin(i['value'], Pin.IN, Pin.PULL_UP) for i in inputs]
        self.pinsOut = [Pin(i['value'], Pin.OUT, value=0) for i in outputs]
        self.inputsSavedState = [i.value() for i in self.pinsIn]
        self.listener = None

    def loop(self):
        if self.listener == None:
            return
        for i in range(len(self.inputs)):
            newValue = self.pinsIn[i].value()
            if newValue != self.inputsSavedState[i]:
                self.listener.pinStateChanged(
                    self.inputs[i]['label'], newValue)
                self.inputsSavedState[i] = newValue
