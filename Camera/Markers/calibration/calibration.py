# Import required modules
import cv2
import numpy as np
import os
import glob

import datetime
  
  
# Define the dimensions of checkerboard
CHECKERBOARD = (5, 8)
  
  
# stop the iteration when specified
# accuracy, epsilon, is reached or
# specified number of iterations are completed.
criteria = (cv2.TERM_CRITERIA_EPS + 
            cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
  
  
# Vector for 3D points
threedpoints = []
  
# Vector for 2D points
twodpoints = []
  
  
#  3D points real world coordinates
objectp3d = np.zeros((1, CHECKERBOARD[0] 
                      * CHECKERBOARD[1], 
                      3), np.float32)
objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],
                               0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None

  
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 630)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
start = datetime.datetime.now()

while (datetime.datetime.now() - start).total_seconds() < 30:
    if int((datetime.datetime.now() - start).total_seconds()) % 10 == 0:
        print((datetime.datetime.now() - start).total_seconds())
    ret, img = vid.read()
    grayColor = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
    # Find the chess board corners
    # If desired number of corners are
    # found in the image then ret = true
    ret, corners = cv2.findChessboardCorners(
                    grayColor, CHECKERBOARD, 
                    cv2.CALIB_CB_ADAPTIVE_THRESH 
                    + cv2.CALIB_CB_FAST_CHECK + 
                    cv2.CALIB_CB_NORMALIZE_IMAGE)
  
    # If desired number of corners can be detected then,
    # refine the pixel coordinates and display
    # them on the images of checker board
    if ret == True:
        threedpoints.append(objectp3d)
  
        # Refining pixel coordinates
        # for given 2d points.
        corners2 = cv2.cornerSubPix(
            grayColor, corners, (11, 11), (-1, -1), criteria)
  
        twodpoints.append(corners2)
  
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, 
                                          CHECKERBOARD, 
                                          corners2, ret)
  
    cv2.imshow('img', img)
    cv2.waitKey(250)
  
cv2.destroyAllWindows()
  
h, w = img.shape[:2]
  
  
# Perform camera calibration by
# passing the value of above found out 3D points (threedpoints)
# and its corresponding pixel coordinates of the
# detected corners (twodpoints)
ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
    threedpoints, twodpoints, grayColor.shape[::-1], None, None)
  
  
# Displaying required output
print(" Camera matrix:")
print(matrix)
#save the matrix in file
np.savetxt('cameraMatrix.txt', matrix, delimiter=',')
  
print("\n Distortion coefficient:")
print(distortion)
#save the matrix in file
np.savetxt('cameraDistortion.txt', distortion, delimiter=',')