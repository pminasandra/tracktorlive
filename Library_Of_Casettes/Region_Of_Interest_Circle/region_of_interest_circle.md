---
title: region_of_interest_circle
author: Isaac Planas-Sitjà
description: Detect when individuals are inside or outside a circular region of interest.
known_issues: Tested only on Linux.
---

```python

# CASSETTE BEGINS: REGION_OF_INTEREST_CIRCLE
# DESCRIPTION: Detect when individuals are inside or outside a circular region of interest.
# AUTHOR: Isaac Planas-Sitjà
# KNOWN ISSUES: Tested only on Linux.
# USER DEFINED VARIABLES:
# Define region of interest (circle)
# parameters
center = (268, 167)  # Centre of the circle
radius = 45          # Radius of the circle
color = (0, 255, 0)  # Green
alpha = 0.5          # Transparency factor

# Draw circle on the overlay

@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    # Draw filled circle on fr
    cv2.circle(fr, center, radius, color, thickness=-1)
    # Blend the circle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)

    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)

# The _in_circle function can be used to trigger Arduino actions, start or stop recording (chunk videos), looming, etc.
def _in_circle(locs, center=center, radius=radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

# CASSETTE ENDS: REGION_OF_INTEREST_CIRCLE
```
