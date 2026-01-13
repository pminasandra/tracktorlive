---
title: print_directions
author: Isaac Planas-Sitjà
description: Calculates and prints the direction based on position changes.
known_issues: None.
---

```python

# CASSETTE BEGINS: PRINT_DIRECTIONS
# DESCRIPTION: Calculates the direction based on position changes.
# AUTHOR: Isaac Planas-Sitjà
# USER DEFINED VARIABLES:
direction = 10 # number of pixels that the animal needs to move before updating position (avoid noise)
dir2 = direction**2
prev = None

@client
def get_angle(data, clock):
    global direction, prev
    if prev is None or np.isnan(prev).any():
        prev=data[0, :, -1]
        return
    else:
        coords = data[0, :, -1]
        Xt=coords[0] - prev[0]
        Yt=coords[1] - prev[1]
        distance2 = Xt**2 + Yt**2
        # if the distance moved is higher than X pixels we update direction and previous position
        if distance2 > int(dir2):
            angle=math.degrees(math.atan2(Yt,Xt)) %360
            prev=data[0, :, -1]
            print(f"{clock}: {angle} degrees.")
            
# CASSETTE ENDS: DIRECTION
```
