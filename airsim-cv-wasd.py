#!/usr/bin/env python3

# In settings.json first activate computer vision mode:
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

import airsim
import numpy as np
import time
import numpy as np
from threading import Lock
from copy import deepcopy
from pynput import keyboard
from pynput import mouse


class InputController():
    def __init__(self, position_step=1.0, angle_step_deg=5.0):
        self.__position_step = position_step
        self.__angle_step_deg = angle_step_deg

        self.__pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.__last_x = 0
        self.__last_y = 0
        self.__received_new_pose = False
        self.__mouse_listener = None
        self.__keyboard_listener = None
        
        self.__input_lock = Lock()

        self.start()


    def __del__(self):
        self.stop()

    def start(self):
        self.__start_keyboard_listener()
        self.__start_mouse_listener()

    def stop(self):
        with self.__input_lock:
            if self.__mouse_listener:
                self.__mouse_listener.stop()
            if self.__keyboard_listener:
                self.__keyboard_listener.stop()

    def get_pose(self) -> list:
        with self.__input_lock:
            self.__received_new_pose = False
            return deepcopy(self.__pose)

    def received_new_pose(self) -> bool:
        return self.__received_new_pose

    def __on_press(self, key):
        with self.__input_lock:
            x = str(key)
            x = x.strip("''")

            if x == 'Key.esc':
                print("Exiting mode")
                return False
            # Use up and down to move in X axis
            elif x == 'w':
                self.__pose[0] += self.__position_step
            elif x == 's':
                self.__pose[0] -= self.__position_step
            # Use left and right to move in Y axis
            elif x == 'a':
                self.__pose[1] -= self.__position_step
            elif x == 'd':
                self.__pose[1] += self.__position_step
            # Use q and a to move in Z axis
            elif x == 'Key.space':
                self.__pose[2] += self.__position_step
            elif x == 'c':
                self.__pose[2] -= self.__position_step
            elif x == 'e':
                self.__pose[4] += self.__position_step
            elif x == 'q':
                self.__pose[4] -= self.__position_step
            else:
                pass

            self.__received_new_pose = True

    def __on_move(self, x, y):
        # print(self.__last_x, x, self.__last_y, y)
        with self.__input_lock:
            self.__pose[5] -= self.__angle_step_deg * (self.__last_x - x) / abs(self.__last_x - x + 0.0000001)
            self.__pose[3] += self.__angle_step_deg * (self.__last_y - y) / abs(self.__last_y - y + 0.0000001)
            self.__received_new_pose = True
            self.__last_x = x
            self.__last_y = y

    def __start_keyboard_listener(self):
        with self.__input_lock:
            if not self.__keyboard_listener:
                self.__keyboard_listener = keyboard.Listener(on_press=self.__on_press, on_release=None)
                self.__keyboard_listener.start()

    def __start_mouse_listener(self):
        with self.__input_lock:
            if not self.__mouse_listener:
                self.__mouse_listener = mouse.Listener(on_move=self.__on_move)
                self.__mouse_listener.start()

    def listener_alive(self) -> bool:
        return self.__mouse_listener.is_alive() and self.__keyboard_listener.is_alive()




if __name__ == "__main__":

    # Run Airsim
    client = airsim.VehicleClient()
    client.confirmConnection()

    # Set pose of camera at 0,0,0 of vehicle
    client.simSetCameraPose("0", airsim.Pose(
        airsim.Vector3r(0.0, 0.0, 0.0), 
        airsim.to_quaternion(0.0, 0.0, 0.0)
        )
    )


    # There we go
    # controller = KeyboardController(1.0, 5.0, os.getcwd(), False)
    controller = InputController(0.1, 5)
    while(controller.listener_alive()):
        if (controller.received_new_pose()):
            new_pose = controller.get_pose()
            curr_position = airsim.Vector3r(new_pose[0], new_pose[1], -1.0 * new_pose[2])

            client.simSetVehiclePose(
                airsim.Pose(curr_position, airsim.to_quaternion(np.deg2rad(new_pose[3]), np.deg2rad(new_pose[4]), np.deg2rad(new_pose[5]))), 
                True
            )

        time.sleep(0.01)

    client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0.0, 0.0, -50.0), 
                                                    airsim.to_quaternion(0.0, 0.0, 0.0)), True)

