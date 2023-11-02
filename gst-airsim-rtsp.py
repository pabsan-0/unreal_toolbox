#! /usr/bin/python3

import airsim
from ctypes import *
import sys
import numpy as np
import json
import cv2 
from threading import Lock 

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtp', '1.0')
from gi.repository import Gst, GLib




def on_bus_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
    mtype = message.type
    
    if mtype == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()

    elif mtype == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(err, debug)
        loop.quit()

    elif mtype == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print(err, debug)
        
    return True


_pts = 0  # buffers presentation timestamp
_duration = 10**9 / 30  # frame duration
_mutex = Lock()

def on_need_data_cb (appsrc, length, u_data):
    global _pts
    global _duration
    global mutex

    camera_id = u_data
    with _mutex:
        png_image = client.simGetImage(camera_id, airsim.ImageType.Scene)
        png_bytes = airsim.string_to_uint8_array(png_image)
    
    buffer = Gst.Buffer.new_wrapped(png_bytes)
    _pts += _duration
    buffer.pts = _pts
    buffer.duration = _duration

    appsrc.emit("push-buffer", buffer)

    return None


if __name__ == "__main__":
    
    ## Airsim part
    
    client = airsim.VehicleClient()
    client.confirmConnection()    
    
    # Unreal will crash if these strings have something other than ints
    camera_ids = ["0", "1", "2", "3"]

    PI = 22/7
    client.simSetCameraPose(camera_ids[0], airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(0.0, 0.0, 0.0) #radians
    ))
    client.simSetCameraPose(camera_ids[1], airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(PI/2, 0.0, 0.0) #radians
    ))
    client.simSetCameraPose(camera_ids[2], airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(PI, 0.0, 0.0) #radians
    ))
    client.simSetCameraPose(camera_ids[3], airsim.Pose(
            airsim.Vector3r(0.0, 0.0, 0.0), 
            airsim.to_quaternion(PI*3/2, 0.0, 0.0) #radians
    ))
   
    # sample an image to get height/width
    img = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene)])[0]
     

    ## Gstreamer part

    Gst.init(sys.argv[1:])
    loop = GLib.MainLoop()
    
    pipe_desc = ""
    for idx, val in enumerate(camera_ids):
        pipe_desc += f"""
            appsrc  emit-signals=true 
                    is-live=true
                    name=my_appsrc_{idx}
                    caps=image/png,width={img.width},height={img.height}
                    format=GST_FORMAT_TIME
                    block=true
                ! decodebin ! video/x-raw
                ! queue
                ! videoconvert 
                ! queue
                ! x264enc tune=zerolatency
                ! queue
                ! rtspclientsink
                    payloader=_pay_{idx}
                    location=rtsp://127.0.0.1:8554/cam{val}
                    protocols=udp
                    latency=0 sync=1 async=0
                rtph264pay name=_pay_{idx}
            """
    print(pipe_desc)

    # Parsing and setting stuff up
    pipeline = Gst.parse_launch(pipe_desc)

    # Listening to the bus for events and errors
    bus = pipeline.get_bus()    
    bus.add_signal_watch()
    bus.connect("message", on_bus_message, loop)

    # Using the appsrc
    for idx, val in enumerate(camera_ids):
        element = pipeline.get_by_name(f"my_appsrc_{idx}")
        element.connect("need-data", on_need_data_cb, val)

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)
    try:
        # Blocking run call 
        loop.run()
    except Exception as e:
        print(e)
        loop.quit()

    # Python has a garbage collector, but normally we'd clean up here
    pipeline.set_state(Gst.State.NULL)
    del pipeline
