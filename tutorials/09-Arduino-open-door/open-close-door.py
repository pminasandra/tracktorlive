# Pranav Minasandra/Isaac Planas-Sitjà
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
import time

import tracktorlive as trl


def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        manu = (port.manufacturer or "").lower()
        if 'ttyUSB' in port.device or 'ser' in desc or 'arduino' in manu or 'arduino' in desc:
            return port.device
    raise RuntimeError('No arduino device could be found')


with open("pillbug.json") as f:
    params = json.load(f)
params["fps"] = 30

server, semm = trl.spawn_trserver(4,
                                params=params,
                                n_ind = 2,
                                realtime=True,
                                buffer_size = 1,
                                draw=True,
                                feed_id="insectinthehouse"
                            )


#Mask area (rectangle)
x1, y1 = 205, 40
x2, y2 = 570, 300

@server
def add_mask(server):
    frame = server.current_frame
    if frame is None:
        return
    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype = np.uint8)
    cv2.rectangle(mask, (x1,y1), (x2,y2), 255, -1)
    frame[mask == 0] = 0

#define area of interest
top_left = (262, 74)
bottom_right = (390, 230)
color = (0, 255, 0)  # Green
alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

top = 74
right = 390
bottom = 230
left = 262

def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
    return left < locs[0] < right and top < locs[1] < bottom
    
# Define circle parameters
# ~ center = (268, 167)  # Centre of the circle
# ~ radius = 45          # Radius of the circle
# ~ color = (0, 255, 0)  # Green
# ~ alpha = 0.5          # Transparency factor


# Draw rectangle on the overlay

@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    #rectangle
    cv2.rectangle(fr, top_left, bottom_right, color, thickness=-1)
    # Draw filled circle on fr
    # ~ cv2.circle(fr, center, radius, color, thickness=-1)
    # Blend the circle or rectangle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)

    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)

client = trl.spawn_trclient("insectinthehouse")

port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)

door_open = False
lastTrigger = 0
count = 0 
@client
def send_to_arduino_open(data, clock):
    global door_open, lastTrigger, count
    curr_loc = data[:,:,-1]
    all_in = all(_in_rect(ant) for ant in curr_loc)
    now = time.time()
    if all_in and not door_open and now - lastTrigger > 5:#animal just moved into the rectangle
        ser.write(b'm')
        print("pillbugs in the house")
        door_open = True
        lastTrigger = time.time()
    
    elif not all_in and door_open and now-lastTrigger > 5:
        count += 1
        if count > 30: #we wait some time before moving the door
            ser.write(b'k')
            print("pillbugs out")
            door_open = False
            lastTrigger = time.time()
            count = 0

trl.run_trsession(server, semm, client)
del client
del server
