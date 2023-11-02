#! /usr/bin/python3

import airsim
from ctypes import *
import sys
import numpy as np
import json
import cv2

PI = 22/7


if __name__ == "__main__":
    
    
    client = airsim.VehicleClient()
    client.confirmConnection()

    client.simSetCameraPose("0", airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(0.0, 0.0, 0.0) #radians
    ))

    client.simSetCameraPose("1", airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(PI/2, 0.0, 0.0) #radians
    ))

    client.simSetCameraPose("2", airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(PI, 0.0, 0.0) #radians
    ))
    
    client.simSetCameraPose("3", airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(PI*3/2, 0.0, 0.0) #radians
    ))


    dec = lambda img: cv2.imdecode(airsim.string_to_uint8_array(img), cv2.IMREAD_UNCHANGED)
    
    images = []
    for ii in range(4):
        images.append(dec(client.simGetImage(str(ii), airsim.ImageType.Scene)))
        cv2.imshow(str(ii), cv2.pyrDown(images[ii]))
        cv2.waitKey(5)

    input("Enter to quit.")
    cv2.destroyAllWindows()
