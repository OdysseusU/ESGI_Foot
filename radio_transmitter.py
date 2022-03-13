# Add your Python code here. E.g.
from microbit import *
import radio
import struct

radio.on()
radio.config(length=32,channel=42,power=7,address=0x31415926)

uart.init(baudrate=115200)

msg = bytes(0)
nb_teams = 1

while True:
    if uart.any():
        msg = uart.read()
        
        v1 = 0
        v2 = 0
        
        for i in range(nb_teams):
            ind = msg[i*5]
            if len(msg) >(i*5 + 1):
                v1 = struct.unpack('H',msg[(i*5+1):(i*5+3)])[0]
            if len(msg) > (i*5 + 3):
                v2 = struct.unpack('H',msg[(i*5+3):(i*5+5)])[0]
            
            radio.config(group=ind)
            radio.send(msg)
            
            display.scroll(v1,wait=False)
        
    sleep(100)
