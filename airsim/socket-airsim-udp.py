#! /usr/bin/python3

import airsim
import numpy as np
import socket 
import cv2
import time 


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
requests = [
    airsim.ImageRequest("0", airsim.ImageType.Scene, False, False),
]

def read_color_image(data_array, height, width):
    img1d = np.frombuffer(data_array, dtype=np.uint8)
    img_rgb = img1d.reshape(height, width, 3)
    return img_rgb


def udpsink(frame_rgb, uri=None):
    """ Make the heatmap available through an udp socket 
    gst-launch-1.0 udpsrc port=5005 ! decodebin ! videoconvert ! autovideosink
    """
    uri = uri if uri else "127.0.0.1:5005" 
    # frame_rgb = np.stack([frame_mono for __ in range(3)], -1)
    frame_jpg = cv2.imencode('.jpg', frame_rgb)[1].tobytes()
    address, port = uri.split(":")
    sock.sendto(frame_jpg, (address, int(port)))


def get_images(client):

    responses = client.simGetImages(requests)
    for res in responses:
        if (res.compress):
            print("Unable to read compressed images. Change ImageRequest settings.")
            continue

        elif (res.image_type == airsim.ImageType.Scene):
            img_rgb = read_color_image(res.image_data_uint8, res.height, res.width)
            img_rgb = cv2.pyrDown(img_rgb)
            udpsink(img_rgb)
        else:
            print("Error: Unrecognized image type: {}".format(res.image_type))
            return



if __name__ == "__main__":
    client = airsim.VehicleClient()
    client.confirmConnection()

    while 1:
        get_images(client)
        time.sleep(0.01)

    





