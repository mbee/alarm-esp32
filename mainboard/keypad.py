import time
from log import log

# Highly inspired from git@github.com:revk/SolarSystem.git


def csum(bla):
    temp = 0xaa
    for b in bla:
        temp = temp + b
    result = (((temp & 0xff000000) >> 24) + ((temp & 0xff0000) >>
                                             16) + ((temp & 0xff00) >> 8) + (temp & 0xff)) & 0xff
    return result


def byteToChar(b):
    chars = "0123456789BAEX*#"
    return chars[b]


class Commands(object):
    def __init__(self, name, length, default):
        self.name = name
        self.length = 0
        self.data = [default]*length
        self.state = False

    def set(self, b):
        self.state = b

    def get(self):
        return self.state


class Keypad(object):

    def __init__(self, uart):
        self.cmd = 0
        self.online = False
        self.display = Commands("display", 32, 0)
        self.keyclick = Commands("keyclick", 1, 5)
        self.sounder = Commands("sounder", 2, 0)
        self.backlight = Commands("backlight", 1, 1)
        self.cursor = Commands("cursor", 2, 0)
        self.blink = Commands("blink", 1, 0)
        self.send0b = False
        self.send07c = False
        self.toggle07 = False
        self.toggle0b = False
        self.lastkey = 0x7f
        self.rs485fault = 0
        self.force = False
        self.rxwait = 0
        self.now = time.ticks_ms()
        self.keyhold = 0
        self.firstKey = True
        self.uart = uart

    def loop(self):
        self.now = time.ticks_ms()

        data = bytearray()
        while self.uart.any() != 0:
            rx = self.uart.read(1)
            if rx != None and len(rx) > 0:
                data.append(rx[0])

        if len(data) > 0:
            self.rxwait = 0
            i = 0
            self.analyzeRX(data)

        if self.rxwait != 0 and (self.rxwait - self.now) > 0:
            return

        if self.rxwait != 0:
            self.rs485fault += 1
            if self.rs485fault > 2:
                log("ERROR: NO RESPONSE FROM RS485")
                self.online = False

        # Write the data
        self.rxwait = self.now + 1000
        data = self.getTX()
        data.append(csum(data))
        self.uart.write(data)

    def analyzeRX(self, data):
        p = len(data)
        if p < 2:
            self.rs485fault += 1
            if self.rs485fault > 2:
                log("Five bad RX consecutive from the keypad")
                self.online = False
            return

        self.rs485fault = 0

        # log("[cmd#{:02x}] received ".format(self.cmd) +
        #     ':'.join('{:02x}'.format(x) for x in data))

        if self.cmd == 0x00 and data[1] == 0xFF and p >= 5:
            if not self.online:
                self.firstKey = True
                self.online = True
                self.toggle0b = True
                self.toggle07 = True
            return

        if data[1] == 0xfe:
            if not self.send0b:
                if self.lastkey & 0x80:
                    if self.keyhold - self.now < 0:
                        self.keyReleased(byteToChar(self.lastkey & 0x0f))
                        self.lastkey = 0x7f
                else:
                    self.lastkey = 0x7f

            return

        if self.cmd == 0x06 and data[1] == 0xf4 and p >= 3:
            if data[2] & 0x40:
                self.caseOpen()
            if not self.send0b:
                if data[2] == 0x7f:
                    if self.lastkey & 0x80:
                        if self.keyhold - self.now < 0:
                            self.keyReleased(byteToChar(self.lastkey & 0x0f))
                            self.lastkey = 0x7f
                    else:
                        self.lastkey = 0x7f
                else:
                    self.send0b = True
                    if self.lastkey & 0x80 and (data[2] != self.lastkey or self.firstKey):
                        self.keyReleased(byteToChar(self.lastkey & 0x0f))
                    if not (data[2] & 0x80) or (data[2] != self.lastkey and not self.firstKey):
                        if data[2] & 0x80:
                            self.keyOnHold(byteToChar(data[2] & 0x0f))
                        else:
                            self.keyPressed(byteToChar(data[2] & 0x0f))
                    if data[2] & 0x80:
                        self.keyhold = self.now + 2000  # add two seconds
                    self.lastkey = data[2]
                    self.firstKey = False

    def getTX(self):
        data = bytearray()
        data.append(0x10)
        if self.force or self.rs485fault or not self.online:
            self.display.set(True)
            self.cursor.set(True)
            self.blink.set(True)
            self.send0b = False
            self.sounder.set(True)
            self.backlight.set(True)
            self.keyclick.set(True)
        if not self.online:
            data.append(0x00)
            data.append(0x0e)
        elif self.send0b:
            self.send0b = False
            data.append(0x0b)
            data.append((0x00, 0x02)[self.toggle0b])
            self.toggle0b = not self.toggle0b
        elif self.lastkey >= 0x7f and (self.display.get() or self.cursor.get() or self.blink.get() or self.send07c):
            data.append(0x07)
            data.append(0x01 | (0x00, 0x08)[self.blink.data[0] & 0x01 != 0] | (
                0x00, 0x80)[self.toggle07])
            if self.cursor.length > 0:
                data.append(0x07)
            if self.display.length > 0:
                data.append(0x1f)
                for n in range(0, 32):
                    if not (n & 0x0f):
                        data.append(0x03)
                        data.append((0x00, 0x40)[n != 0])
                    if (n < self.display.length):
                        data.append(self.display.data[n])
                    else:
                        data.append(ord(' '))
            else:
                data.append(0x17)
            if self.cursor.get() or self.cursor.length > 0:
                data.append(0x03)
                data.append((0x00, 0x40)[self.cursor.data[0] &
                                         0x10 != 0]+self.cursor.data[0] & 0x0f)
                if self.cursor.data[0] & 0x80:
                    data.append(0x06)  # solid block
                elif self.cursor.data[0] & 0x40:
                    data.append(0x10)  # underline
            self.toggle07 = not self.toggle07
            if self.display.get():
                self.send07c = True  # always send twice
            else:
                self.cursor.set(False)
                self.blink.set(False)
                self.send07c = False
            self.display.set(False)
            # log("[cmd#{:02x}] sending ".format(self.cmd) +
            #     ':'.join('{:02x}'.format(x) for x in data))
        elif self.keyclick.get():
            self.keyclick.set(False)
            data.append(0x19)
            data.append(self.keyclick.data[0] & 0x07)
            data.append(0x00)
        elif self.sounder.get():
            self.sounder.set(False)
            data.append(0x0c)
            if self.sounder.length > 0:
                if self.sounder.data[1]:
                    data.append(0x03)
                else:
                    data.append(0x01)
            else:
                data.append(0x00)
            data.append(self.sounder.data[0] & 0x3f)
            data.append(self.sounder.data[1] & 0x3f)
        elif self.backlight.get():
            self.backlight.set(False)
            data.append(0x0d)
            data.append(self.backlight.data[0] & 0x01)
        else:
            data.append(0x06)
        self.cmd = data[1]

        return data

    def setDisplay(self, s):
        for i in range(0, len(s)):
            self.display.data[i] = ord(s[i])
        self.display.length = len(s)
        self.display.set(True)

    def keyPressed(self, key):
        if self.listener != None:
            self.listener.keyPressed(key)

    def keyReleased(self, key):
        if self.listener != None:
            self.listener.keyReleased(key)

    def keyOnHold(self, key):
        if self.listener != None:
            self.listener.keyOnHold(key)

    def caseOpen(self, key):
        if self.listener != None:
            self.listener.caseOpen(key)
