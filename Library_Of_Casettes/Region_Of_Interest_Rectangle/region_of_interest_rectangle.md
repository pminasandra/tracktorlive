---
title: region_of_interest_rectangle
author: Isaac Planas-Sitjà
description: Detect when individuals are outside (inside) a rectangular region of interest.
known_issues: Tested only on Linux.
---

```python

# CASSETTE BEGINS: REGION_OF_INTEREST_RECTANGLE
# DESCRIPTION: Detect when individuals are outside (inside) a rectangular region of interest.
# AUTHOR: Isaac Planas-Sitjà
# KNOWN ISSUES: Tested only on Linux.
# USER DEFINED VARIABLES:
# Define area of interest (rectangular)
# Edges of the area in pixels
top = 120
right = 300
bottom = 350
left = 150

# Choose colour and transparency factor
color = (0, 255, 0)  # Green
alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

# Coordinates
top_left = (left, top)
bottom_right = (right, bottom)

# Display the region of interest on screen (this is not visible in recorded videos; to do so please combine with other cassettes: e.g. take a look at timestamp cassettes)
# Draw rectangle on the overlay
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    #rectangle
    cv2.rectangle(fr, top_left, bottom_right, color, thickness=-1)
    # Blend the rectangle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)

    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)

# The _in_rect and _out_rect functions can be used to trigger Arduino actions, start or stop recording (chunk videos), looming, etc.
# In this cassette we check if the individual has crossed the right edge, so only the X position is considered; the Y position is ignored.

def _out_rect(locs, right=right):
    return locs[0,0] > right

# def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
#    return left < locs[0] < right and top < locs[1] < bottom

# CASSETTE ENDS: REGION_OF_INTEREST_RECTANGLE
```
