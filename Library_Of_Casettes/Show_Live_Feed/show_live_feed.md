---
title: show_live_feed
author: Pranav Minasandra
description: Displays current tracking from the server in real-time. Press 'q' or <Esc> to close running display at any time.
issues: Does not work on Max due to fork/spawn issues.
---

```python
# CASSETTE BEGINS: SHOW_LIVE_FEED
# DESCRIPTION: Displays current tracking from the server in real-time.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES: None
# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.
@server.startfunc
def show_live_feed_setup(server):
    server.show_flag = True
    cv2.namedWindow(server.feed_id, cv2.WINDOW_NORMAL)

@server
def show_live_feed_show(server):
    if server.show_flag:
        frame = server.framesbuffer[-1]
        if frame is None:
            return
        cv2.imshow(server.feed_id, server.framesbuffer[-1])
        key = cv2.waitKey(1)

        if key==27 or key==ord('q'):
            server.show_flag = False
            cv2.destroyWindow(server.feed_id)

@server.stopfunc
def show_live_feed_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(server.feed_id)
# CASSETTE ENDS: SHOW_LIVE_FEED
```
