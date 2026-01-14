---
title: gaussian_blur
author: Pranav Minasandra
description: Apply a Gaussian blur to each frame before tracking.
known_issues: none
---

```
# CASSETTE BEGINS: GAUSSIAN_BLUR
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Apply a Gaussian blur to each frame before tracking.
# USER SPECIFIABLE DETAILS
GAUSSIAN_BLUR_KSIZE = 21    # must be odd; e.g. 3, 5, 7
GAUSSIAN_BLUR_SIGMA = 0    # 0 lets OpenCV choose based on kernel size
# KNOWN ISSUES: None

@server
def gaussian_blur(server):
    k = int(GAUSSIAN_BLUR_KSIZE)
    if k <= 1 or k % 2 == 0:
        return
    server.current_frame = cv2.GaussianBlur(
        server.current_frame,
        (k, k),
        GAUSSIAN_BLUR_SIGMA
    )

# CASSETTE ENDS: GAUSSIAN_BLUR
```
