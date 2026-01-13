---
title: update_plot
author: Isaac Planas-Sitjà
description: Displays (and saves) a plot every few seconds. Useful to monitor data in real time.
known_issues: None.
---

```python

# CASSETTE BEGINS: UPDATE_PLOT
# DESCRIPTION: Displays (and saves) a plot every few seconds. Useful to monitor data in real time.
# AUTHOR: Isaac Planas-Sitjà
# USER DEFINED VARIABLES:
client = trl.spawn_trclient("update_plot")

# Shared buffer
all_speeds = []
all_times = []
# User params:
VEL_CALC_NUM_FRAMES = 5
checkpoints = 2 # in seconds

@client
def average_speed(data, clock):
    global all_speeds, all_times
    coords = data[0, :, -VEL_CALC_NUM_FRAMES:]
    times = clock[-VEL_CALC_NUM_FRAMES:]

    if np.isnan(coords).any() or np.isnan(times).any():
        return

    diffs = np.diff(coords, axis=1)
    dists = np.linalg.norm(diffs, axis=0)
    dt = times[-1] - times[0]
    if dt > 0:
        avg_speed = np.sum(dists) / dt
        all_speeds.append(avg_speed)
        all_times.append(times[-1])
    else:
        all_speeds.append(0)
        all_times.append(times[-1])
    plt.ion()
    if int(times[-1]) % checkpoints == 0:
        plt.clf()
        plt.scatter(all_times, all_speeds, s=8)
        plt.xlabel('Time (s)')
        plt.ylabel('Average speed (px/s)')
        plt.tight_layout()
        plt.savefig('./ex1_fig1a.eps', format='eps', dpi=300)
        plt.pause(0.001)
# CASSETTE ENDS: UPDATE_PLOT
```
