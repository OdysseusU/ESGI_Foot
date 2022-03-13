#! /usr/bin/env python3

import serial
import signal
import sys, getopt
import time
import struct
import numpy as np

import cv2

import serial.tools.list_ports

def handler(signum, frame):
    res = input("\nCtrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        cv2.destroyAllWindows()
        exit(1)

signal.signal(signal.SIGINT, handler)


def get_color_position(hsv, range1, range2):
    mask = cv2.inRange(hsv, (40, 50, 50), (90, 250, 230))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (24, 24))
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        area = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(area)

        return x,y,w,h,area
    return None,None,None,None,None


def main(argv):
    serial_port = '/dev/cu.usbmodem11302'
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

    if ser:
        ser.open()

    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 630)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, img = vid.read()

    now = round(time.time() * 1000)
    timer1 = now
    fps = 30.0
    countDown_serial = 500

    list_positions = [(0,0)]
    while True:
        ret, img = vid.read()

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        x,y,w,h,area = get_color_position(hsv, (40,50,50), (90,250,230))

        if area is not None:
            list_positions[0] = (x+w//2,y+h//2)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            img = cv2.drawContours(img, area, -1, (0, 0, 255), 3)

        cv2.imshow('frame', img)

        if now - timer1 > countDown_serial:
            for ind,v in enumerate(list_positions):
                print(ind,v[0],v[1])
                if ser:
                    ser.write(bytes(ind) + struct.pack('H',v[0])+struct.pack('H',v[1]))
            timer1 = now

        frame_time = round(time.time() * 1000) - now
        delay = round(1000.0/fps - frame_time)
        if delay < 1:
            delay = 1

        now = round(time.time() * 1000)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
               break


if __name__ == "__main__":
   main(sys.argv[1:])
