---
title: record_when_together
author: Pranav Minasandra
description: When two animals are close together, record video only then.
known_issues: None.
---

```python

# CASSETTE BEGINS: RECORD_WHEN_TOGETHER
# DESCRIPTION: When two animals are close together, record video only then.
# AUTHOR: Pranav Minasandra
# NOTES: If there is a lot of noise, a rule can be defined to record only when animals have been together for more than X frames (MIN_FRAMES_TOGETHER = 30).
# USER DEFINED VARIABLES:
THRESH_APPROACH_DIST = 300 #px: record only when animals closer than this
THRESH_MIN_DIST = 100 #px: but don't record when animals detected closer than this!
THRESH_STOP_DIST = 400 #px: stop recording when they are farther away than this.


# Internals
THRESH_MIN_DIST2 = THRESH_MIN_DIST**2
THRESH_APPROACH_DIST2 = THRESH_APPROACH_DIST**2 #px**2
THRESH_STOP_DIST2 = THRESH_STOP_DIST**2

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

    elif dist2 > THRESH_STOP_DIST2:#when animals go far away again
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
```
