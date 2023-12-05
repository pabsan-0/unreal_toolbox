#! /usr/bin/python3

import airsim
import cv2
import pprint
from ctypes import *
import sys

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

def on_need_data_cb (appsrc, length, u_data):
    global _pts
    global _duration

    image_factory = u_data
    img = image_factory()
    
    buffer = Gst.Buffer.new_wrapped(cv2.imencode(".png", img)[1].tobytes())
    _pts += _duration
    buffer.pts = _pts
    buffer.duration = _duration

    appsrc.emit("push-buffer", buffer)

    return None


if __name__ == "__main__":
    
    ## Airsim part

    client = airsim.VehicleClient()
    client.confirmConnection()

    camera_name = "0"
    image_type = airsim.ImageType.Scene

    client.simSetDetectionFilterRadius(camera_name, image_type, 200 * 100) 
    client.simAddDetectionFilterMeshName(camera_name, image_type, "Chair*") 
    client.simAddDetectionFilterMeshName(camera_name, image_type, "Talon*") 
    def image_factory(get_size=False):
            rawImage = client.simGetImage(camera_name, image_type)
            if not rawImage:
                return

            # Would be AWESOME to **map** the bytes to a numpy array, paint over
            #   them in-place, and send them their way
            png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
            cylinders = client.simGetDetections(camera_name, image_type)
            if cylinders:
                for cylinder in cylinders:
                    s = pprint.pformat(cylinder)
                    cv2.rectangle(png,(int(cylinder.box2D.min.x_val),int(cylinder.box2D.min.y_val)),(int(cylinder.box2D.max.x_val),int(cylinder.box2D.max.y_val)),(255,0,0),2)
                    cv2.putText(png, cylinder.name, (int(cylinder.box2D.min.x_val),int(cylinder.box2D.min.y_val - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12))
            
            if get_size:
                return png.shape[0], png.shape[1]
            else:
                return png
             
    # Get a first image to check sizes
    height, width = image_factory(get_size=True)
    

    ## Gstreamer part

    Gst.init(sys.argv[1:])
    loop = GLib.MainLoop()
    
    pipe_desc = f"""
        appsrc  emit-signals=true 
                is-live=true
                name=my_appsrc
                caps=image/png,width={width},height={height}
                format=GST_FORMAT_TIME
                block=true
            ! queue max-size-buffers=4 
            ! pngdec
            ! videoconvert 
            ! fpsdisplaysink sync=0 async=0
        """

    # Parsing and setting stuff up
    pipeline = Gst.parse_launch(pipe_desc)

    # Listening to the bus for events and errors
    bus = pipeline.get_bus()    
    bus.add_signal_watch()
    bus.connect("message", on_bus_message, loop)

    # Using the appsrc
    element = pipeline.get_by_name("my_appsrc")
    element.connect("need-data", on_need_data_cb, image_factory)


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

