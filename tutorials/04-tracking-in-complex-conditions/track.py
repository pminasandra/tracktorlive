# Pranav Minasandra
# pminasandra.github.io
# 22 Oct 2025

import json

import cv2
import numpy as np
import tracktorlive as trl

with open("true-params.json") as f:
    params = json.load(f)

server, semm = trl.spawn_trserver("ant.mp4",
                        params=params,
                        realtime=False,
                        feed_id='record_ant',
                        write_recordings=True)

# CASSETTE BEGINS: EXTRACT_SPECIFIED_FRAMES
# DESCRIPTION: Saves as jpg all frames at specified indices.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
extract_specified_frames_ids = [100] #indices
# KNOWN ISSUES: None
@server
def extract_specified_frames(server):
    index = int(server.frame_index)
    if index in extract_specified_frames_ids:
        cv2.imwrite(f"{server.feed_id}_fr_{index}.jpg",
                    server.current_frame)
# CASSETTE ENDS: EXTRACT_SPECIFIED_FRAMES


# CASSETTE BEGINS: ADD_CIRCULAR_MASK
# DESCRIPTION: Masks everything except a circle of specified position and radius.
# AUTHOR: Vivek H Sridhar Pranav Minasandra
# USER DEFINED VARIABLES:
# Coordinates of circle center (px):
add_circular_mask_x = 495
add_circular_mask_y = 267
# Circle radius (px):
add_circular_mask_radius = 180
# KNOWN ISSUES: None
@server
def add_mask(server):
    frame = server.current_frame
    if frame is None:
        return
    mask = np.zeros((frame.shape[0], frame.shape[1]))
    cv2.circle(mask, (add_circular_mask_x, add_circular_mask_y), add_circular_mask_radius, 255, -1)
    frame[mask == 0] = 0
# CASSETTE ENDS: ADD_CIRCULAR_MASK


# CASSETTE BEGINS: BOOST_CONTRAST
# DESCRIPTION: Brightness and contrast control
# AUTHOR: Vivek H Sridhar Pranav Minasandra
# USER DEFINED VARIABLES:
boost_contrast_ALPHA = 1.8  # Contrast control (1.0–3.0)
boost_control_BETA = 0     # Brightness adjustment control (0–100)
@server
def boost_contrast(server):
    server.current_frame = cv2.convertScaleAbs(server.current_frame,
                                                alpha=boost_contrast_ALPHA,
                                                beta=boost_control_BETA
                                            )
# CASSETTE ENDS: BOOST_CONTRAST

trl.run_trsession(server, semm)

