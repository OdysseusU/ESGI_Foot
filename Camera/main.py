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

def get_serial(argv):
    serial_port = '/dev/cu.usbmodem11302'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('main.py -s <serial_port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -s <serial_port>')
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
    return ser

signal.signal(signal.SIGINT, handler)
def get_pose():
    return 0,0,0

def get_position(camera_matrix, depth, px, py):
    x = (px-camera_matrix[0][2]) * depth / camera_matrix[0][0]
    y = (py-camera_matrix[1][2]) * depth / camera_matrix[1][1]
    return (x,y)

def main(argv):
    ser = get_serial(argv)
    #read matrix
    matrix = np.loadtxt('cameraMatrix.txt', delimiter=',')
    depth = 0.71#meters


    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 630)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    ret, img = vid.read()

    now = round(time.time() * 1000)
    timer1 = now
    fps = 30.0
    countDown_serial = 100

#    list_positions = [(0,0,theta),(0,0)]
    while True:

        data = {}
        ret, img = vid.read()


        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        (corners, ids, rejected) = detector.detectMarkers(img)
        
        if ids is not None:
            print(ids)
            combined = list(zip(ids, corners))
            sorted_combined = sorted(combined, key=lambda x: x[0])
            sorted_ids, sorted_corners = zip(*sorted_combined)

            for (corner, id_r) in zip(sorted_corners, sorted_ids):
                corners = corner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                cv2.line(img, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(img, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(img, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(img, bottomLeft, topLeft, (0, 255, 0), 2)

                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                theta = math.atan2(topRight[1] - bottomRight[1], topRight[0] - bottomRight[0])
                pos = get_position(matrix, depth, cX, cY)
                data[id_r[0]] = (pos,theta*180/math.pi)


        if now - timer1 > countDown_serial:
            res = bytes()
            if bool(data):
                for d in data.items():
                    res += int(d[0]).to_bytes(1, byteorder='big') + struct.pack('h', int(d[1][0][0]*1000)) + struct.pack('h', int(d[1][0][1]*1000)) + struct.pack('h', int(d[1][1]*100))
                if ser:
                    ser.write(res)
                timer1 = now

        cv2.imshow('frame', img)

        frame_time = round(time.time() * 1000) - now
        delay = round(1000.0/fps - frame_time)
        if delay < 1:
            delay = 1

        now = round(time.time() * 1000)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
               break
    cv2.destroyAllWindows()


if __name__ == "__main__":
   main(sys.argv[1:])
