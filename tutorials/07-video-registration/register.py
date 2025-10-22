import json
import multiprocessing as mp
from os.path import join as joinpath
import os
mp.set_start_method('fork')

import cv2
import numpy as np

import tracktorlive as trl


CROP_WIDTH, CROP_HEIGHT = 200, 200
CROPPED_DIR = "centered-clips"
os.makedirs(CROPPED_DIR, exist_ok=True)

with open("termite-params.json") as f:
    params = json.load(f)

server, semm = trl.spawn_trserver(
                "termite_video.mp4",
                params,
                n_ind=8,
                feed_id="termite_video",
                realtime=False,
                draw=False
)


# CASETTE BEGINS: ADD_CIRCULAR_MASK
# DESCRIPTION: Maska excluding a circle at specified center with specified radius.
# AUTHOR: Vivek H Sridhar Pranav Minasandra
# USER DEFINED VARIABLES:
# Coordinates of circle center (px):
add_circular_mask_offset_x = -18
add_circular_mask_offset_y = -5
# Circle radius (px):
add_circular_mask_radius = 520
# KNOWN ISSUES: None
@server
def add_mask(server):
    frame = server.current_frame
    if frame is None:
        return
    mask = np.zeros((frame.shape[0], frame.shape[1]))
    cv2.circle(mask, (mask.shape[1]//2 + add_circular_mask_offset_x, mask.shape[0]//2 +
    add_circular_mask_offset_y), add_circular_mask_radius, 255, -1)
    frame[mask == 0] = 0
# CASETTE ENDS: ADD_CIRCULAR_MASK



# Mac users, please delete this casette.
# CASETTE BEGINS: SHOW_LIVE_FEED
# DESCRIPTION: Displays current tracking from the server in real-time.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES: None
# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.
@server.startfunc
def show_live_feed_setup(server):
    server.draw = True
    server.show_flag = True
    cv2.namedWindow(wname, cv2.WINDOW_NORMAL)

@server
def show_live_feed_show(server):
    if server.show_flag:
        frame = server.framesbuffer[-1]
        if frame is None:
            return
        cv2.imshow(wname, server.framesbuffer[-1])
        key = cv2.waitKey(1)

        if key==27 or key==ord('q'):
            server.show_flag = False
            cv2.destroyWindow(wname)

@server.stopfunc
def show_live_feed_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(wname)
# CASETTE END: SHOW_LIVE_FEED

@server
def crop_to_center(server):
    data, _ = server.get_data_and_clock()
    pos = data[4, :, -1]

    if np.any(np.isnan(pos)):
        return

    if np.any(pos < 0):
        return

    x, y = int(pos[0]), int(pos[1])
    frame = server.framesbuffer[-1]
    if frame is None:
        return
    h, w = frame.shape[:2]

    x1 = max(x - CROP_WIDTH // 2, 0)
    y1 = max(y - CROP_HEIGHT // 2, 0)
    x2 = min(x1 + CROP_WIDTH, w)
    y2 = min(y1 + CROP_HEIGHT, h)
    x1 = max(x2 - CROP_WIDTH, 0)
    y1 = max(y2 - CROP_HEIGHT, 0)

    crop = frame[y1:y2, x1:x2]
    if crop.shape[:2] != (CROP_HEIGHT, CROP_WIDTH):
        return

    if not hasattr(server, "crop_writer") or server.crop_writer is None:
        outpath = joinpath(CROPPED_DIR, f"centered-{server.feed_id}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        server.crop_writer = cv2.VideoWriter(outpath, fourcc, server.fps, (CROP_WIDTH, CROP_HEIGHT))

    server.crop_writer.write(crop)

@server.stopfunc
def close_crop_writer(server):
    if hasattr(server, "crop_writer") and server.crop_writer is not None:
        server.crop_writer.release()
        server.crop_writer = None

trl.run_trsession(server, semm)

