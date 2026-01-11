---
title: dynamic_masking
author: Pranav Minasandra
description: Only look for individuals in vicinity of previous locs
known_issues: none
---


```python
# CASSETTE BEGINS: DYNAMIC_MASKING
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Only look for individuals in vicinity of previous locs
# USER SPECIFIABLE DETAILS
DYNMASK_BUFFER_AREA_RADIUS = 100 #px
# KNOWN ISSUES: None

@server
def dynamic_masking(server):
    data, clock = server.get_data_and_clock()

    # Most recent locs given by data[:, :, -1]  -> N×2 array (x, y) per individual
    locs = data[:, :, -1]

    # If any values are -1 or NaN, return without modifying the frame
    # (treat any negative coordinate as invalid, per TracktorLive conventions)
    if (
        locs.size == 0
        or np.isnan(locs).any()
        or (locs < 0).any()
    ):
        return

    frame = server.current_frame
    if frame is None:
        return

    H, W = frame.shape[:2]
    r = int(DYNMASK_BUFFER_AREA_RADIUS)
    if r <= 0:
        return

    # Build a boolean mask of pixels to KEEP
    keep = np.zeros((H, W), dtype=bool)

    # Draw filled circles around each (x, y) using a bounded local distance check
    r2 = r * r
    for x_f, y_f in locs:
        # locs are (x, y); convert to int pixel indices
        x0 = int(round(float(x_f)))
        y0 = int(round(float(y_f)))

        # Bounding box for the circle (clipped to frame)
        x_min = max(0, x0 - r)
        x_max = min(W - 1, x0 + r)
        y_min = max(0, y0 - r)
        y_max = min(H - 1, y0 + r)

        if x_min > x_max or y_min > y_max:
            continue

        ys = np.arange(y_min, y_max + 1)[:, None]
        xs = np.arange(x_min, x_max + 1)[None, :]
        keep[y_min:y_max + 1, x_min:x_max + 1] |= ((xs - x0) ** 2 + (ys - y0) ** 2) <= r2

    # Mask out everything except the union of circles
    if frame.ndim == 2:
        server.current_frame = np.where(keep, frame, 0)
    else:
        out = frame.copy()
        out[~keep] = 0
        server.current_frame = out

# CASSETTE ENDS: DYNAMIC_MASKING
```
