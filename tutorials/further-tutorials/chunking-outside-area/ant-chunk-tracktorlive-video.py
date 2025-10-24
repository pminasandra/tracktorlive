# Pranav Minasandra/Isaac Planas-Sitjà
# 29 Apr 2025
# pminasandra.github.io

"""
Example code that will save the recording only when the ant is outside of a specific area (e.g., outside of the nest).
"""

import json
import multiprocessing as mp
mp.set_start_method('fork')

import cv2
import numpy as np
import os
import ulid
from os.path import join as joinpath

import tracktorlive as trl

with open("p-ant.json") as f:
    params = json.load(f)
params["fps"] = 30

os.makedirs("ant-chunked", exist_ok=True)

server, semm = trl.spawn_trserver("./ant-video-chunking.mp4",
                                params=params,
                                n_ind = 1,
                                realtime=False,
                                buffer_size = 1,
                                draw=False,
                                feed_id="insectinthehouse"
                            )

#mask
mask_offset_x = 20
mask_offset_y = -5

@server
def add_mask(server):
    frame = server.current_frame
    if frame is None:
        return
    mask = np.zeros((frame.shape[0], frame.shape[1]))
    cv2.circle(mask, (mask.shape[1]//2 + mask_offset_x, mask.shape[0]//2 + mask_offset_y), 190, 255, -1)
    frame[mask == 0] = 0


top = 60
right = 500
bottom = 500
left = 295

top_left = (left, top)
bottom_right = (right, bottom)
color = (0, 255, 0)  # Green
alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

#show
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    cv2.rectangle(fr, top_left, bottom_right, color, thickness=-1)
    cv2.addWeighted(fr, 0.3, fr2, 0.7, 0, fr2)
    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)

client = trl.spawn_trclient("insectinthehouse")

#define area out
def _out_rect(locs, right=right):
    return locs[0,0] > right
    
    
# We will now write a function to do the chunking based on the zone:
# Global variable to track how long animals have been inside/outside the nest
frames_outside_thresh = 0
MIN_FRAMES_OUTSIDE = 30  # minimum frames animals must be outside

frames_inside_thresh = 0
MIN_FRAMES_INSIDE = 30  # minimum frames animals must be inside

@server
def chunking(server):
    global frames_outside_thresh, frames_inside_thresh
    data, _ = server.get_data_and_clock()
    curr_vals = data[:,:,-1]
    prev_vals = data[:,:,-2]

    if np.any(curr_vals < 0.0):
        # unknown location
        return None
    if _out_rect(curr_vals):#ant just moved out the rectangle
        frames_inside_thresh = 0  # reset counter
        frames_outside_thresh += 1
        if frames_outside_thresh >= MIN_FRAMES_OUTSIDE: 
            if len(server.recorded_frames) == 0:
                server.keep_video.value = True
                print("recording in progress...")
    else:
        if len(server.recorded_frames) > 0:
            frames_inside_thresh += 1
            if frames_inside_thresh >= MIN_FRAMES_INSIDE:
                server.keep_video.value = False
                frames_outside_thresh = 0  # reset after dump
                frames_inside_thresh = 0  # reset after dump
                fname = f'chunk-{ulid.ULID()}.avi'
                server.dumpvideo(joinpath('ant-chunked', fname))

# Since this is recording from a video, we need to handle end-of-file events
# However, this bit isn't relevant in real-time applications.
@server.stopfunc#adding this decorator makes it a server-side termination functionality
def final_chunk(server):
    if len(server.recorded_frames) > 0:
        server.keep_video.value=False
        fname = f'chunk-{ulid.ULID()}.avi'
        server.dumpvideo(joinpath('ant-chunked', fname))
        
trl.run_trsession(server, semm)

