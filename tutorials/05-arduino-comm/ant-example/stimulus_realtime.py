# Pranav Minasandra / Isaac Planas-Sitjà
# 29 Apr 2025
# pminasandra.github.io

"""
Example code that triggers when an individual is within a certain part of the screen
"""

import json
import multiprocessing as mp
mp.set_start_method('fork')

import cv2
import serial
import serial.tools.list_ports
import numpy as np

import tracktorlive as trl


def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        manu = (port.manufacturer or "").lower()
        if 'ttyUSB' in port.device or 'ser' in desc or 'arduino' in manu or 'arduino' in desc:
            return port.device
    raise RuntimeError('No arduino device could be found')


with open("insects.json") as f:
    params = json.load(f)
params["fps"] = 30

server, semm = trl.spawn_trserver(4,
                                params=params,
                                n_ind = 1,
                                realtime=True,
                                buffer_size = 1,
                                draw=True,
                                feed_id="insectinthehouse"
                            )

# ~ top_left = (150, 50)
# ~ bottom_right = (300, 200)
# ~ color = (0, 255, 0)  # Green
# ~ alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

# Define circle parameters
center = (268, 167)  # Centre of the circle
radius = 45          # Radius of the circle
color = (0, 255, 0)  # Green
alpha = 0.5          # Transparency factor


# Draw rectangle on the overlay

@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    # ~ cv2.rectangle(fr, top_left, bottom_right, color, thickness=-1)
    # Draw filled circle on fr
    cv2.circle(fr, center, radius, color, thickness=-1)
    # Blend the circle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)
    # ~ cv2.addWeighted(fr, 0.3, fr2, 0.7, 0, fr2)

    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)

client = trl.spawn_trclient("insectinthehouse")

port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)

# ~ top = 50
# ~ right = 300
# ~ bottom = 200
# ~ left = 150

# ~ def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
    # ~ return left < locs[0,0] < right and top < locs[0,1] < bottom

def _in_circle(locs, center=center, radius=radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

@client
def send_to_arduino(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]

    if _in_circle(curr_loc) and not _in_circle(prev_loc):#animal just moved into the rectangle
           ser.write(b'm')

trl.run_trsession(server, semm, client)
del client
del server
