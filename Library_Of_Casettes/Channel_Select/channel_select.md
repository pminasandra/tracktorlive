---
title: channel_select
author: Pranav Minasandra
description: Preserves only one of the BGR channels.
known_issues: None.
---

```python
# CASSETTE BEGINS: CHANNEL_SELECT
# AUTHOR: Pranav Minasandra and Vivek H Sridhar
# DESCRIPTION: Preserves only one of the BGR channels.
# USER SPECIFIABLE DETAILS
channel_select_CHANNEL_NR = 0 #Blue: 0 | Green: 1 | Red: 2
# KNOWN ISSUES: None

@server
def channel_select(server):
    frame_channel = server.current_frame[:,:,channel_select_CHANNEL_NR]
    for i in range(3):
        if i != channel_select_CHANNEL_NR:
            server.current_frame[:,:,i] = frame_channel
# CASSETTE ENDS: CHANNEL_SELECT
```
