---
title: display_with_circ_hl
author: Pranav Minasandra
description: Displays current tracking from the server in real-time. Highlights a chosen circular region. Press 'q' or <Esc> to close running display at any time.
issues: Does not work on Macs due to fork/spawn issues.
---

```python
# CASSETTE BEGINS: DISPLAY_WITH_CIRC_HL
# DESCRIPTION: Displays current tracking from the server in real-time with a
#   circular highlight of a user-defined colour.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
dwchl_center = (268, 167)
dwchl_radius = 45
dwchl_color = (0, 255, 0)  # Green
dwchl_alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.

@server.startfunc
def dwchl_setup(server):
    server.show_flag = True
    cv2.namedWindow(server.feed_id, cv2.WINDOW_NORMAL)

# Draw rectangle on the overlay
@server
def dwchl_show(server):
    if not server.show_flag:
        return
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    cv2.circle(fr, dwchl_center, dwchl_radius, dwchl_color, thickness=-1)
    cv2.addWeighted(fr, dwchl_alpha, fr2, 1 - dwchl_alpha, 0, fr2)

    cv2.imshow(server.feed_id, fr2)
    key = cv2.waitKey(1)

    if key==27 or key==ord('q'):
        server.show_flag = False
        cv2.destroyWindow(server.feed_id)

@server.stopfunc
def dwchl_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(server.feed_id)
# CASSETTE ENDS: DISPLAY_WITH_RECT_HL
```
