#!/usr/bin/env python3

from microbit import *
import radio
import struct

class radio_transmitter:
    def __init__(self):
        radio.on()
        radio.config(length=32,channel=42,power=7,address=0x31415926, group=0)
    
        uart.init(baudrate=115200)
        self.msg = bytes(0)
        
    def receive_and_send(self):
        if uart.any():
            self.msg = uart.read()
            radio.send(self.msg)
            
    def update(self):
        self.receive_and_send()

class radio_receiver:
    def __init__(self):
        radio.on()
        radio.config(length=32,channel=42,power=7,address=0x31415926, group=0)
        
        self.positions = {}
        
    def parse_poses(self,msg):
        self.positions = {}
        if msg and len(msg) > 0:
            len_msg = 7
            for i in range(len(msg)//len_msg):
                smsg = i*len_msg
                id_v = int.from_bytes(msg[smsg], 'big')
                v1 = struct.unpack('h',msg[smsg+1:smsg+3])[0]
                v2 = struct.unpack('h',msg[smsg+3:smsg+5])[0]
                th = struct.unpack('h',msg[smsg+5:smsg+7])[0]
                self.positions[id_v] = (v1,v2,th)
        return self.positions
        
    def update(self):
        self.parse_poses(radio.receive())
