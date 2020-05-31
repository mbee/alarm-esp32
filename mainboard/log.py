import time


def log(msg):
    ts = time.ticks_ms()
    print("["+str(ts)+"] " + msg + "\n")
