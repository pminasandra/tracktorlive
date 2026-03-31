---
title: invert_frame
author: Pranav Minasandra (with TracktorLive Cassette Maker GPT)
description: Inverts incoming frames
known_issues: none
---

```python
# CASSETTE BEGINS: INVERT_FRAMES
# DESCRIPTION: Inverts incoming frames (pixel-wise negative).
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES: None
# KNOWN ISSUES: None

@server
def invert_frames(server):
    # server.current_frame is the frame before tracking :contentReference[oaicite:0]{index=0}
    server.current_frame = 255 - server.current_frame

# CASSETTE ENDS: INVERT_FRAMES
```
