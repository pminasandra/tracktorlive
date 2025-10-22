---
title: boost_contrast
author: Vivek H Sridhar and Pranav Minasandra
description: Brightness and contrast control.
known_issues: None.
---

```python
# CASSETTE BEGINS: BOOST_CONTRAST
# DESCRIPTION: Brightness and contrast control.
# AUTHOR: Vivek H Sridhar and Pranav Minasandra
# USER DEFINED VARIABLES:
boost_contrast_ALPHA = 1.8  # Contrast control (1.0–3.0)
boost_control_BETA = 0     # Brightness adjustment control (0–100)
@server
def boost_contrast(server):
    server.current_frame = cv2.convertScaleAbs(server.current_frame,
                                                alpha=boost_contrast_ALPHA,
                                                beta=boost_control_BETA
                                            )
# CASSETTE ENDS: BOOST_CONTRAST
```
