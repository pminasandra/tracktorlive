---
title: background_subtract
author: Pranav Minasandra
description: Replace background pixels with white using an averaged background image.
---

```python
# CASSETTE BEGINS: BACKGROUND_SUBTRACT
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Replace background pixels with white using an averaged background image.
# USER SPECIFIABLE DETAILS
BACKGROUND_IMAGES = [
    "bg1.png",
    "bg2.png",
]
BG_THRESHOLD = 25  # 0..255

# precompute averaged background once, at cassette load time
_bg_acc = None
for p in BACKGROUND_IMAGES:
    img = cv2.imread(p, cv2.IMREAD_COLOR)  # user ensures correct size/channels
    if img is None:
        raise FileNotFoundError(f"Could not read background image: {p}")
    img = img.astype(np.float32)
    _bg_acc = img if _bg_acc is None else (_bg_acc + img)

BG_AVG = (_bg_acc / float(len(BACKGROUND_IMAGES))).astype(np.uint8)

@server
def background_subtract(server):
    frame = server.current_frame  # assume uint8, 3-channel
    if frame is None:
        return

    diff = cv2.absdiff(frame, BG_AVG)
    mask_bg = (diff.max(axis=2) <= BG_THRESHOLD)  # background-like pixels

    out = frame.copy()
    out[mask_bg] = 255  # background -> white
    server.current_frame = out

# CASSETTE ENDS: BACKGROUND_SUBTRACT
```
