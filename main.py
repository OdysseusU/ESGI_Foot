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


def get_color_position(hsv, range1, range2):
    mask = cv2.inRange(hsv, (40, 50, 50), (90, 250, 230))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (24, 24))
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        area_list = sorted(contours, key=cv2.contourArea, reverse=True)
        area_list = [area_list[i] for i in range(min(len(area_list), 3))]

        res = []

        for a in area_list:
            x, y, w, h = cv2.boundingRect(a)
            res.append((x, y, w, h))

        return res
    return None,None,None,None,None

def get_pose(list_areas):
    if len(list_areas) == 3:
        p1 = list_areas[0]
        p2 = list_areas[1]
        p3 = list_areas[2]

        p1p2 = math.sqrt(sum([(p1[i] - p2[i])**2 for i in range(2)]))
        p2p3 = math.sqrt(sum([(p2[i] - p3[i])**2 for i in range(2)]))
        p3p1 = math.sqrt(sum([(p3[i] - p1[i])**2 for i in range(2)]))

        index_min = min(range(len(3)), key=[p1p2, p2p3, p3p1].__getitem__)
        #TODO
    else:
        return 0,0,0


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

    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 630)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, img = vid.read()

    now = round(time.time() * 1000)
    timer1 = now
    fps = 30.0
    countDown_serial = 500

    list_positions = [(0,0),(0,0)]
    while True:
        ret, img = vid.read()

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        list_points = get_color_position(hsv, (40,50,50), (90,250,230))

        if list_points is not None:
            pose = get_pose(list_points)
            list_positions[0] = (pose[0],pose[1])
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            img = cv2.drawContours(img, (list_points[0])[4], -1, (0, 0, 255), 3)

        cv2.imshow('frame', img)

        if now - timer1 > countDown_serial:
            res = bytes()
            for ind, v in enumerate(list_positions):
                # print(ind,v[0],v[1])
                res += (ind).to_bytes(1, byteorder='big') + struct.pack('H', v[0]) + struct.pack('H', v[1])
            if ser:
                ser.write(res)
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
