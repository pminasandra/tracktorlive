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

with open("pillbug.json") as f:
    params = json.load(f)

server, semm = trl.spawn_trserver(4,
                                params=params,
                                n_ind = 2,
                                realtime=True,
                                buffer_size = 1,
                                draw=True,
                                feed_id="insectinthehouse"
                            )


# CASETTE BEGINS: ADD_RECTANGULAR_MASK
# DESCRIPTION: Masks everything except a rectangle of specified vertices
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
# Rectangle coordinates:
add_rectangular_mask_top, add_rectangular_mask_left = 205, 40
add_rectangular_mask_bottom, add_rectangular_mask_right = 570, 300

@server
def add_rectangular_mask(server):
    frame = server.current_frame
    mask = np.zeros(frame.shape)
    mask = cv2.rectangle(mask, (add_rectangular_mask_top, add_rectangular_mask_left),
                        (add_rectangular_mask_bottom, add_rectangular_mask_right),
                        (255,255,255),
                        -1)
    frame[mask ==  0] = 0
# CASETTE ENDS: ADD_RECTANGULAR_MASK

top = 74
right = 390
bottom = 230
left = 262


# CASSETTE BEGINS: DISPLAY_WITH_RECT_HL
# DESCRIPTION: Displays current tracking from the server in real-time with a
#   rectangular highlight of a user-defined colour.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
dwrhl_top_left = (top, left)
dwrhl_bottom_right = (bottom, right)
dwrhl_color = (0, 255, 0)  # Green
dwrhl_alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.

@server.startfunc
def dwrhl_setup(server):
    server.show_flag = True
    cv2.namedWindow(server.feed_id, cv2.WINDOW_NORMAL)

# Draw rectangle on the overlay
@server
def dwrhl_show(server):
    if not server.show_flag:
        return
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    cv2.rectangle(fr, dwrhl_top_left, dwrhl_bottom_right, dwrhl_color, thickness=-1)
    cv2.addWeighted(fr, dwrhl_alpha, fr2, 1 - dwrhl_alpha, 0, fr2)

    cv2.imshow(server.feed_id, fr2)
    key = cv2.waitKey(1)

    if key==27 or key==ord('q'):
        server.show_flag = False
        cv2.destroyWindow(server.feed_id)

@server.stopfunc
def dwrhl_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(server.feed_id)
# CASSETTE ENDS: DISPLAY_WITH_RECT_HL


def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
    return left < locs[0] < right and top < locs[1] < bottom

client = trl.spawn_trclient("insectinthehouse")

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        manu = (port.manufacturer or "").lower()
        if 'arduino' in desc or 'arduino' in manu:
            return port.device
    raise RuntimeError('No arduino device could be found')

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
