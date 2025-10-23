---
title: add_circular_mask
author: Pranav Minasandra and Vivek H Sridhar
description: Masks everything except a rectangle of specified vertices.
known_issues: None.
---

```python
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
```
