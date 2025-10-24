
"""
Example script to chunk video data only when animals approach close by.
"""

import multiprocessing as mp
import os
from os.path import join as joinpath

import cv2
import json
import numpy as np
import ulid

import tracktorlive as trl

# This demonstrates how to chunk input from video sources, retaining
# only videos where animals are in proximity. Here we will use a video,
# but this is only for demonstration. This is practically intended for
# cases when interactions are rare and a real-time tracktorserver is run.
# In this video example, we use Zerg Ultralisks engaging in combat, a common
# scene from the video game Starcaft: Brood War (1998) to act as a proxy for
# animal interactions.

# All copyrights and licenses to the imagery in the video belongs to Blizzard
# and is used here only for instructional purposes.

with open("brood-war-params.json") as f:
    params = json.load(f)

os.makedirs("ultralisks-chunked", exist_ok=True)

server, semm = trl.spawn_trserver("./ultralisks.mp4",
                                    params=params,
                                    n_ind=2,
                                    realtime=False,
                                    buffer_size=1#just need a second before interactions
                                )

# CASSETTE BEGINS: RECORD_WHEN_TOGETHER
# DESCRIPTION: When two animals are close together, record video only then.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
THRESH_APPROACH_DIST = 300 #px: record only when animals closer than this
THRESH_MIN_DIST = 100 #px: but don't record when animals detected closer than this!


# Internals
THRESH_MIN_DIST2 = THRESH_MIN_DIST**2
THRESH_APPROACH_DIST2 = THRESH_APPROACH_DIST**2 #px**2
@server
def record_when_together(server):
    data, _ = server.get_data_and_clock()
    curr_vals = data[:,:,-1]

    if np.any(curr_vals < 0.0):
        # we don't know the location of some individuals
        return None

    dist2 = ((curr_vals[0,:] - curr_vals[1,:])**2).sum()
    if THRESH_MIN_DIST2 < dist2 <= THRESH_APPROACH_DIST2:
        if len(server.recorded_frames) == 0:#nothing stored yet?
            server.keep_video.value = True

    elif dist2 > THRESH_APPROACH_DIST2:
        if len(server.recorded_frames) > 0:
            server.keep_video.value=False
            fname = f'chunk-{ulid.ULID()}.{trl.rcParams["file_format"]}'
            server.dumpvideo(joinpath('ultralisks-chunked', fname))

# We need to handle end-of-file events
@server.stopfunc
def final_chunk(server):
    if len(server.recorded_frames) > 0:
        server.keep_video.value=False
        fname = f'chunk-{ulid.ULID()}.{trl.rcParams["file_format"]}'
        server.dumpvideo(joinpath('ultralisks-chunked', fname))
# CASSETTE ENDS: RECORD_WHEN_TOGETHER

trl.run_trsession(server, semm)
