---
title: add_circular_mask
author: Pranav Minasandra and Vivek H Sridhar
description: Masks everything except a circle of specified position and radius.
known_issues: None.
---

```python
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
```
