
# Quickstart

You’ll need:

-    A video file with reasonably clear contrast (e.g. top-down fish or insect
    footage). Tracktor's adaptive thresholding makes it reasonably resilient to
    background disturbances especially when tracking one individual.

-    A parameter JSON file defining thresholds and filters for tracking (see
    example below for how to generate one)

If you are very new to all this, you will need to be at least somewhat familiar
with Python to be able to use TracktorLive. You don't need to know much computer
vision. A basic python tutorial can be found
[here](https://docs.python.org/3/tutorial/index.html).

Let us create a simple python script to demonstrate TracktorLive. Your python script will be as follows:

```python
import json
import time
import numpy as np
import tracktorlive as trl

# Load tracking parameters
with open("params.json") as f:
    params = json.load(f)

# Start a server to track one individual
server, semm = trl.spawn_trserver("video.mp4", params, n_ind=1, realtime=False)

# Start a client for real-time access to tracking data
client = trl.spawn_trclient(feed_id=server.feed_id)

# Define what the client should do each polling cycle
@client
def print_coords(data, clock):
    coords = data[0, :, -1] #the latest coordinates of the individual
    t = clock[-1] # latest timestamp
    if np.all(coords >= 0):
        print(f"t = {t:.2f}s, x = {coords[0]:.1f}, y = {coords[1]:.1f}")

# Run server and client together
trl.run_trsession(server, semm, client)

```

We will cover how to create an appropriate 'params.json' file later.
In this example, a TracktorServer handles all the tracking needed,
and using the print_coords casette, a TracktorClient handles the response (in this case,
the response is simply 'always print the coordinates to a screen').



[previous](01-overview.md) | [next](03-installation.md)
