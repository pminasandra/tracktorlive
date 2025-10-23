# Pranav Minasandra
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

import tracktorlive as trl


with open("mouse-params.json") as f:
    params = json.load(f)

server, semm = trl.spawn_trserver("./mouse_video.mp4",
                                params=params,
                                n_ind = 1,
                                realtime=False,
                                buffer_size = 1,
                                draw=True,
                                feed_id="mouseinthehouse",
                                use_kmeans=False
                            )


# CASSETTE BEGINS: DISPLAY_WITH_RECT_HL
# DESCRIPTION: Displays current tracking from the server in real-time with a 
#   rectangular highlight of a user-defined colour.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
dwrhl_top_left = (150, 50)
dwrhl_bottom_right = (300, 200)
dwrhl_color = (0, 255, 0)  # Green
dwrhl_alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque


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

client = trl.spawn_trclient("mouseinthehouse")


# CASSETTE BEGINS: MESSAGE_ARDUINO
# DESCRIPTION: When a user-defined function returns a character, transmits that
# character to a connected Arduino.
# AUTHOR: Isaac Planas-Sitjà and Pranav Minasandra
# USER DEFINED VARIABLES:

# First, define a 'condition_func' function that returns either a character or None.
top = 50
right = 300
bottom = 200
left = 150

def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
    return left < locs[0,0] < right and top < locs[0,1] < bottom

def condition_func(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]
    if _in_rect(curr_loc) and not _in_rect(prev_loc):#mouse just moved into the rectangle
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
