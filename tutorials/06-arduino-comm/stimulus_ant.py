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

with open("insects.json") as f:
    params = json.load(f)

server, semm = trl.spawn_trserver(4,
                                params=params,
                                n_ind = 1,
                                realtime=True,
                                buffer_size = 1,
                                draw=True,
                                feed_id="insectinthehouse"
                            )

# CASSETTE BEGINS: DISPLAY_WITH_CIRC_HL
# DESCRIPTION: Displays current tracking from the server in real-time with a
#   circular highlight of a user-defined colour.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
dwchl_center = (268, 167)
dwchl_radius = 45
dwchl_color = (0, 255, 0)  # Green
dwchl_alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.

@server.startfunc
def dwchl_setup(server):
    server.show_flag = True
    cv2.namedWindow(server.feed_id, cv2.WINDOW_NORMAL)

# Draw rectangle on the overlay
@server
def dwchl_show(server):
    if not server.show_flag:
        return
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    cv2.circle(fr, dwchl_center, dwchl_radius, dwchl_color, thickness=-1)
    cv2.addWeighted(fr, dwchl_alpha, fr2, 1 - dwchl_alpha, 0, fr2)

    cv2.imshow(server.feed_id, fr2)
    key = cv2.waitKey(1)

    if key==27 or key==ord('q'):
        server.show_flag = False
        cv2.destroyWindow(server.feed_id)

@server.stopfunc
def dwchl_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(server.feed_id)
# CASSETTE ENDS: DISPLAY_WITH_RECT_HL

client = trl.spawn_trclient("insectinthehouse")

# CASSETTE BEGINS: MESSAGE_ARDUINO
# DESCRIPTION: When a user-defined function returns a character, transmits that
# character to a connected Arduino.
# AUTHOR: Isaac Planas-Sitjà and Pranav Minasandra
# USER DEFINED VARIABLES:

# First, define a 'condition_func' function that returns either a character or None.
def _in_circle(locs, center=dwchl_center, radius=dwchl_radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

# Then, return 'm' if the ant is in the circle.
def condition_func(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]
    if _in_circle(curr_loc) and not _in_circle(prev_loc):#ant just moved into the circle
       return 'm'
    return None

# Then we will set up the Arduino etc.
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

# Below cassette handles transmission.
@client
def message_arduino(data, clock):
    char = condition_func(data, clock)
    if char is not None:
        ser.write(bytes(char, "utf8"))

# CASSETTE ENDS: MESSAGE_ARDUINO

trl.run_trsession(server, semm, client)
