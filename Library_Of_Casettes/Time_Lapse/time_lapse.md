---
title: time_lapse
author: Pranav Minasadra
description: Build a time-lapse by subsampling frames into a custom buffer and writing once at the end.
known_issues: none
---

```python
# CASSETTE BEGINS: TIME_LAPSE
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Build a time-lapse by subsampling frames into a custom buffer and writing once at the end.
# USER SPECIFIABLE DETAILS
TOTAL_REAL_TIME = 60.0          # seconds of real time covered
TIMELAPSE_VIDEO_DURATION = 5.0  # seconds of output video
TIMELAPSE_OUTFILE = "timelapse.mp4"
# KNOWN ISSUES: None

@server.startfunc
def timelapse_start(server):
    server._timelapse_frames = []
    server._timelapse_last_t = None
    server._timelapse_dt = float(TOTAL_REAL_TIME) / float(TIMELAPSE_VIDEO_DURATION * server.fps)

@server
def timelapse(server):
    import numpy as np
    _, clock = server.get_data_and_clock()
    t = clock[-1]
    if np.isnan(t):
        return

    if server._timelapse_last_t is None or (t - server._timelapse_last_t) >= server._timelapse_dt:
        frame = server.current_frame
        if frame is not None:
            server._timelapse_frames.append(frame.copy())
            server._timelapse_last_t = t

@server.stopfunc
def timelapse_end(server):
    import cv2
    import numpy as np
    import os.path
    from os.path import join as joinpath

    frames = getattr(server, "_timelapse_frames", [])
    if len(frames) == 0:
        return

    H, W = frames[0].shape[:2]
    out_fps = max(1.0, len(frames) / float(TIMELAPSE_VIDEO_DURATION))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    outfile = joinpath(server.feed_id, TIMELAPSE_OUTFILE)
    if not os.path.exists(server.feed_id):
        import os
        os.makedirs(server.feed_id)
    vw = cv2.VideoWriter(outfile, fourcc, out_fps, (W, H))

    for f in frames:
        if f is None:
            continue
        if f.ndim == 2:
            f = cv2.cvtColor(f, cv2.COLOR_GRAY2BGR)
        if f.shape[0] != H or f.shape[1] != W:
            f = cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA)
        vw.write(f)

    vw.release()

# CASSETTE ENDS: TIME_LAPSE

```
