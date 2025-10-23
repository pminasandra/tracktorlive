---
title: add_circular_mask
author: Pranav Minasandra and Vivek H Sridhar
description: Masks everything except a circle of specified position and radius.
known_issues: None.
---

```python
# CASETTE BEGINS: ADD_CIRCULAR_MASK
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
def add_circular_mask(server):
    frame = server.current_frame
    if frame is None:
        return
    mask = np.zeros((frame.shape[0], frame.shape[1]))
    cv2.circle(mask, (add_circular_mask_x, add_circular_mask_y), add_circular_mask_radius, 255, -1)
    frame[mask == 0] = 0
# CASETTE ENDS: ADD_CIRCULAR_MASK
```
