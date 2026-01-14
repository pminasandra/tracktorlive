---
title: delayed_start
author: Pranav Minasandra
description: Delay the start of tracking by a fixed amount of time.
known_issues: none
---

```python
# CASSETTE BEGINS: DELAYED_START
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Delay the start of tracking by a fixed amount of time.
# USER SPECIFIABLE DETAILS
DELAY_TIME = 5.0  # seconds
# KNOWN ISSUES: None

@server.startfunc
def delayed_start(server):
    import time
    t = float(DELAY_TIME)
    if t > 0:
        time.sleep(t)

# CASSETTE ENDS: DELAYED_START
```
