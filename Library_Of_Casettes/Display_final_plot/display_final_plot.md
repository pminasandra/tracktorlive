---
title: display_final_plot
author: Isaac Planas-Sitjà
description: Displays and saves a plot when we reach the end of the video file we are analysing.
known_issues: None.
---

```python

# CASSETTE BEGINS: DISPLAY_FINAL_PLOT
# DESCRIPTION: Displays and saves a plot when we reach the end of the video file we are analysing.
# AUTHOR: Isaac Planas-Sitjà
# USER DEFINED VARIABLES:
# Shared buffer
all_speeds = []
all_times = []
# User params:
VEL_CALC_NUM_FRAMES = 5

@server
def average_speed(server):
    global all_speeds, all_times
    data, clock = server.get_data_and_clock()
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
        
@server.stopfunc
def plot_final_avg_speed(server):
    plt.scatter(all_times, all_speeds, s=8)
    plt.xlabel('Time (s)')
    plt.ylabel('Average speed (px/s)')
    plt.tight_layout()
    plt.savefig('./ex1_fig1a.eps', format='eps', dpi=300)
    plt.show()
# CASSETTE ENDS: DISPLAY_FINAL_PLOT
```
