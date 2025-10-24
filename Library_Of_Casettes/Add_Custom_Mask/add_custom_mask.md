---
title: add_custom_mask
author: Pranav Minasandra
description: Add a custom mask to every frame based on user-provided image file.
known_issues: None.
---

**Note:** This cassette relies on a user-defined image provided to the cassette.
This file must be an image of the same dimensions as each frame, and must be
grayscale, with pixels being either fully black or fully white.

```python
# CASSETTE BEGINS: ADD_CUSTOM_MASK
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Masks out a custom, user-defined part of the frame.
## User specifiable details
add_mask_MASK_FILE = "./mask.png" #this file must be only pure black and white
# see provided example file.
# KNOWN ISSUES: None

MASK = cv2.imread(add_mask_MASK_FILE, cv2.IMREAD_GRAYSCALE)

@server
def add_custom_mask(server):
    server.current_frame = cv2.bitwise_and(server.current_frame,
                                            server.current_frame, mask=MASK)

# CASSETTE ENDS: ADD_CUSTOM_MASK
```
