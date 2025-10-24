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
# CASETTE END: SHOW_LIVE_FEED

# CASSETTE BEGINS: FIRST_PERSON_VIEWS
# DESCRIPTION: Generates cropped, rotated videos assuming birds-eye view
# following each separate individual
# AUTHOR: Pranav Minasandra (using ChatGPT 5)
# KNOWN_ISSUES: rotates frames a bit too much sometimes
@server
def crop_all_oriented(server):
    # ---- Tunables (can override via server attributes) ----
    BACK_STEPS = getattr(server, "dir_back_steps", 5)            # uses -1 and -5 for heading
    ALPHA = getattr(server, "dir_smooth_alpha", 0.2)             # EMA smoothing on direction
    SPEED_THRESH = getattr(server, "dir_speed_thresh", 1e-3)     # stationary threshold (pixels/frame)
    MAX_DEG_PER_SEC = getattr(server, "dir_max_deg_per_sec", 180.0)

    # FPS → per-frame rotation cap (protects against sudden spins)
    fps = max(float(getattr(server, "fps", 30.0)), 1.0)
    MAX_DEG_PER_FRAME = MAX_DEG_PER_SEC / fps
    max_rad = np.deg2rad(MAX_DEG_PER_FRAME)

    # ---- State holders (persist between calls) ----
    if not hasattr(server, "_orient"):
        server._orient = {}              # IND -> unit vector heading (ux, uy)
    if not hasattr(server, "_crop_writers"):
        server._crop_writers = {}        # IND -> cv2.VideoWriter

    # ---- Get data and latest frame ----
    data, _ = server.get_data_and_clock()
    if data.shape[2] <= BACK_STEPS:
        return                           # not enough history to estimate heading

    frame = server.framesbuffer[-1]
    if frame is None:
        return

    # Ensure destination directory exists once
    os.makedirs(CROPPED_DIR, exist_ok=True)

    n_ind = int(getattr(server, "n_ind", data.shape[0]))

    for IND in range(n_ind):
        # --- Positions (expects [tracks, 2, time]) ---
        pos_now  = data[IND, :, -1]                # [x, y] latest
        pos_prev = data[IND, :, -BACK_STEPS]       # [x, y] a few frames ago

        # Skip invalid
        if np.any(np.isnan(pos_now)) or np.any(np.isnan(pos_prev)):
            continue
        if np.any(pos_now < 0) or np.any(pos_prev < 0):
            continue

        # --- Motion vector and speed ---
        v = pos_now - pos_prev
        speed = float(np.linalg.norm(v))

        # Previous smoothed direction if available
        has_prev = IND in server._orient

        # Measurement direction (unit); reuse last if “stationary”
        if speed >= SPEED_THRESH:
            u_meas = v / (np.linalg.norm(v) + 1e-12)
        else:
            if not has_prev:
                continue                # no direction yet for this IND
            u_meas = server._orient[IND]

        u_prev = server._orient[IND] if has_prev else u_meas

        # --- (1) EMA smoothing on the unit circle ---
        u_blend = (1.0 - ALPHA) * u_prev + ALPHA * u_meas
        n = np.linalg.norm(u_blend)
        u_blend = u_prev if n < 1e-12 else (u_blend / n)

        # --- (2) Rate-limit the rotation change (deg/frame) ---
        # Signed angle between u_prev and u_blend via atan2(cross, dot)
        dot = float(np.clip(np.dot(u_prev, u_blend), -1.0, 1.0))
        cross = float(u_prev[0]*u_blend[1] - u_prev[1]*u_blend[0])  # z of 2D cross
        delta_rad = np.arctan2(cross, dot)

        if abs(delta_rad) > max_rad:
            step = np.sign(delta_rad) * max_rad
            c, s = np.cos(step), np.sin(step)
            u_smooth = np.array([c*u_prev[0] - s*u_prev[1],
                                 s*u_prev[0] + c*u_prev[1]], dtype=float)
        else:
            u_smooth = u_blend

        # Persist smoothed direction for this IND
        server._orient[IND] = u_smooth

        # --- Build oriented crop (forward points "up") ---
        x, y = float(pos_now[0]), float(pos_now[1])
        alpha_deg = np.degrees(np.arctan2(u_smooth[1], u_smooth[0]))
        theta_deg = alpha_deg + 90.0  # rotate so heading is vertical upward in the crop

        # Rotate about (x, y) and translate so (x, y) lands at crop center
        M = cv2.getRotationMatrix2D((x, y), theta_deg, 1.0)
        M[0, 2] += (CROP_WIDTH  / 2.0 - x)
        M[1, 2] += (CROP_HEIGHT / 2.0 - y)

        crop = cv2.warpAffine(
            frame, M, (CROP_WIDTH, CROP_HEIGHT),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,  # black padding if near borders
        )
        if crop is None or crop.shape[:2] != (CROP_HEIGHT, CROP_WIDTH):
            continue

        # If grayscale, convert to BGR so VideoWriter is consistent
        if len(crop.shape) == 2:
            crop = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)

        # --- Per-individual writer (lazy init) ---
        wr = server._crop_writers.get(IND)
        if wr is None:
            outpath = joinpath(CROPPED_DIR, f"centered-{server.feed_id}-ind{IND:02d}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')             # container/codec pairing for .mp4
            wr = cv2.VideoWriter(outpath, fourcc, fps, (CROP_WIDTH, CROP_HEIGHT))
            server._crop_writers[IND] = wr

        wr.write(crop)


@server.stopfunc
def close_all_crop_writers(server):
    """Release all per-individual writers on shutdown."""
    if hasattr(server, "_crop_writers"):
        for IND, wr in list(server._crop_writers.items()):
            try:
                if wr is not None:
                    wr.release()
            finally:
                server._crop_writers[IND] = None
        server._crop_writers = {}
# CASSETTE ENDS: FIRST_PERSON_VIEWS

trl.run_trsession(server, semm)

