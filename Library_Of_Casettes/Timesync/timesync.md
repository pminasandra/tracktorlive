---
title: timesync
author: Pranav Minasandra
description: Creates a parquet file of time.time() clock, useful for ms level sync.
known_issues: not hardware level clock info.
---

```python
# CASSETTE BEGINS: TIMESYNC
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Creates a parquet file of time.time() clock, useful for ms level sync.
# USER SPECIFIABLE DETAILS

TIMESYNC_CLOCK_OFFSET = 0 #seconds. set to 18 for GPS time, etc.

@server.startfunc
def timesync_fd_start(server):
    server.timesync_obj = [None]
    server.timesync_last_timestamp_pushed = server.timesync_obj[-1]

@server
def timesync(server):
    import numpy as np
    _, clock = server.get_data_and_clock()
    if server.timesync_last_timestamp_pushed is None:
        if np.isnan(clock[-1]):
            return
        else:
            server.timesync_obj.append(server.t_init + clock[-1] + TIMESYNC_CLOCK_OFFSET)
            return

    server.timesync_obj.append(clock[-1] + TIMESYNC_CLOCK_OFFSET)

@server.stopfunc
def timesync_fd_end(server):
    import pandas as pd
    df = pd.DataFrame({"timestampUTC": server.timesync_obj[1:]})
    df.to_parquet(f"{server.feed_id}-timesyncUTC.parquet")

# CASSETTE ENDS: TIMESYNC
```
