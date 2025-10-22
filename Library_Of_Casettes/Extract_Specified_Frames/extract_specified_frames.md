---
title: extract_specified_frames
author: Pranav Minasandra
description: Saves as jpg all frames at specified indices.
known_issues: None.
---

```python
# CASSETTE BEGINS: EXTRACT_SPECIFIED_FRAMES
# DESCRIPTION: saves as jpg all frames at specified indices.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
extract_specified_frames_ids = [100] #indices
# KNOWN ISSUES: None
@server
def extract_specified_frames(server):
    index = int(server.frame_index)
    if index in extract_specified_frames_ids:
        cv2.imwrite(f"{server.feed_id}_fr_{index}.jpg",
                    server.current_frame)
# CASSETTE ENDS: EXTRACT_SPECIFIED_FRAMES
```
