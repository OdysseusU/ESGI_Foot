#!/usr/bin/env python3

import serial
import signal
import sys, getopt
import time
import struct
import math
import numpy as np

import cv2

import serial.tools.list_ports

def handler(signum, frame):
    res = input("\nCtrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        cv2.destroyAllWindows()
        exit(1)

signal.signal(signal.SIGINT, handler)


def main(argv):
    serial_port = '/dev/cu.usbmodem11202'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -s <serial_port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -s <serial_port>')
            sys.exit()
        elif opt in ("-p", "--serial_port"):
            serial_port = arg

    myports = [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]
    ser = None
    if serial_port in myports:
        ser = serial.Serial(serial_port,115200)
        if ser.isOpen():
            ser.close()
    else:
        print("Port doesn't exist")
        print(myports)

    if ser:
        ser.open()

    now = round(time.time() * 1000)
    timer1 = now
    fps = 30.0
    countDown_serial = 500

    list_positions = [(0,1),(0,0)]
    while True:
        if now - timer1 > countDown_serial:
            res = bytes()
            for ind,v in enumerate(list_positions):
                #print(ind,v[0],v[1])
                res += (ind).to_bytes(1,byteorder='big') + struct.pack('H',v[0])+struct.pack('H',v[1])
            if ser:
                ser.write(res)
            timer1 = now

        frame_time = round(time.time() * 1000) - now
        delay = round(1000.0/fps - frame_time)
        if delay < 1:
            delay = 1

        now = round(time.time() * 1000)


if __name__ == "__main__":
   main(sys.argv[1:])
