
"""
Example script to launch a looming video only when fish is moving.
"""

import multiprocessing as mp
import os
from os.path import join as joinpath
import subprocess
import time
mp.set_start_method('fork')

import cv2
import json
import numpy as np
import ulid

import tracktorlive as trl

# This shows how to setup a server-client system to run a specific command, in
# this case play a video, whenever the animal is moving. The video example is
# motivated by presenting looming stimuli, but any shell command can be added in
# its place, e.g., to run equipment, launch web services, etc. Likewise, any
# condition other than velocity can also be programmed.


# First, let's load the parameters.
with open("flume-video-params.json") as f:
    params = json.load(f)


#os.makedirs("ultralisks-chunked", exist_ok=True)
#

server, semm = trl.spawn_trserver("./flume_video.mp4",
                                    params=params,
                                    n_ind=1,
                                    realtime=False,
                                    buffer_size=2#just need a second before interactions
                                )

# First, we need to mask out everyhthing outside region of interest
# CASETTE BEGINS: ADD_RECTANGULAR_MASK
# DESCRIPTION: Masks everything except a rectangle of specified vertices
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
# Rectangle coordinates:
add_rectangular_mask_top, add_rectangular_mask_left = 280, 3
add_rectangular_mask_bottom, add_rectangular_mask_right = 1030, 690

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

# CASETTE BEGINS: SHOW_LIVE_FEED
# DESCRIPTION: Displays current tracking from the server in real-time.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES: None
# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.
@server.startfunc
def show_live_feed_setup(server):
    server.show_flag = True
    cv2.namedWindow(server.feed_id, cv2.WINDOW_NORMAL)

@server
def show_live_feed_show(server):
    if server.show_flag:
        frame = server.framesbuffer[-1]
        if frame is None:
            return
        cv2.imshow(server.feed_id, server.framesbuffer[-1])
        key = cv2.waitKey(1)

        if key==27 or key==ord('q'):
            server.show_flag = False
            cv2.destroyWindow(server.feed_id)

@server.stopfunc
def show_live_feed_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(server.feed_id)
# CASETTE ENDS: SHOW_LIVE_FEED

client = trl.spawn_trclient(server.feed_id)


## We will now write a function to do the velocity based video response on this distance:
# CASSETTE BEGINS: RUN_COMMAND_ON_CONDITION
# DESCRIPTION: Runs a shell command when a function returns True, respecting a time
# based cooldown rule.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
RCOC_RUN_COMMAND = "cvlc --fullscreen --play-and-exit --no-osd ./looming-video.mp4"
RCOC_COMMAND_COOLDOWN = 5 #seconds (if None, no cooldown is imposed)

# Example function: is velocity above some threshold?
VEL_CALC_NUM_FRAMES = 5
THRESHOLD_VEL = 125 #px/s
def _vel_higher(data, clock):
    # Extract recent data
    coords = data[0, :, -VEL_CALC_NUM_FRAMES:]  # shape (2, VEL_CALC_NUM_FRAMES)
    times = clock[-VEL_CALC_NUM_FRAMES:]

    # Skip if any coordinates or timestamps are invalid
    if np.isnan(coords).any() or np.isnan(times).any():
        return

    # Compute displacements and distances
    diffs = np.diff(coords, axis=1)  # shape (2, VEL_CALC_NUM_FRAMES-1)
    dists = np.linalg.norm(diffs, axis=0)  # shape (VEL_CALC_NUM_FRAMES-1,)

    dt = times[-1] - times[0]
    if dt > 0:
        avg_speed = np.sum(dists) / dt
    else:
        return

    return avg_speed > THRESHOLD_VEL

RCOC_CHECK_FUNC = _vel_higher #SET TO ANY FUNCTION OF YOUR CHOICE

# INTERNALS: (DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING)
time_last = mp.Value('d', 0.0)
def _cooldown_satisfied():
    if RCOC_COMMAND_COOLDOWN is None:
        return True
    else:
        return time.time() - time_last.value > RCOC_COMMAND_COOLDOWN

def run_quiet_command(cmd=RCOC_RUN_COMMAND):
    """Run a bash command quietly and block until it completes."""
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=os.environ.copy())


@client
def run_command_on_condition(data, clock):
    if RCOC_CHECK_FUNC(data, clock) and _cooldown_satisfied():
        time_last.value = time.time()
        run_quiet_command()

# CASSETTE ENDS: RUN_COMMAND_ON_CONDITION

trl.run_trsession(server, semm, client)
