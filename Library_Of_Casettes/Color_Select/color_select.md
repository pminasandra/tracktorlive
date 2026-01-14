---
title: color_select
author: Pranav Minasandra
description: Keep only pixels close to a user-defined BGR color; mask out everything else.
known_issues: none
---



```python
# CASSETTE BEGINS: COLOR_SELECT
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Keep only pixels close to a user-defined BGR color; mask out everything else.
# USER SPECIFIABLE DETAILS
COLOR_SELECT_BGR = (0, 0, 175)   # (B, G, R)
COLOR_SELECT_TOL = 63            # tolerance per channel (0–255)
# KNOWN ISSUES: None

@server
def color_selection(server):
    frame = server.current_frame
    if frame is None or frame.ndim != 3:
        return

    import numpy as np

    bgr = np.array(COLOR_SELECT_BGR, dtype=np.int16)
    tol = int(COLOR_SELECT_TOL)

    diff = np.abs(frame.astype(np.int16) - bgr[None, None, :])
    keep = np.all(diff <= tol, axis=2)

    out = frame.copy()
    out[~keep] = 255
    server.current_frame = out

# CASSETTE ENDS: COLOR_SELECTION
```
