---
title: preserve_frame
author: Pranav Minasandra
description: Put non-edited frames in framesbuffer (useful for dumpvideo methods)
known_issues: none
---

```python
# CASETTE BEGINS: PRESERVE_FRAME
# DESCRIPTION: Put non-edited frames in framesbuffer (useful for dumpvideo methods)
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
# KNOWN ISSUES: None
@server
def preserve_frame(server):
    server.preserved_frame = server.current_frame.copy()
    if server.framesbuffer[-1] is None:
        return
    server.framesbuffer[-1] = server.preserved_frame

# CASETTE ENDS: ADD_CIRCULAR_MASK
```
