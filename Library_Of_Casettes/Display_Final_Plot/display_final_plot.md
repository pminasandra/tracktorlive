---
title: display_final_vel_plot
author: Isaac Planas-Sitjà
description: Displays and saves a plot of velocities when we reach the end of the video file we are analysing.
known_issues: None.
---

```python
# CASSETTE BEGINS: DISPLAY_FINAL_VEL_PLOT
# DESCRIPTION: Displays and saves a plot when we reach the end of the video file we are analysing.
# AUTHOR: Isaac Planas-Sitjà
# KNOWN_ISSUES: matplotlib backend errors sometimes.
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
    coords = data[:, :, -VEL_CALC_NUM_FRAMES:]
    times = clock[-VEL_CALC_NUM_FRAMES:]
    dt = times[-1] - times[0]

    if np.isnan(coords).any() or np.isnan(times).any():
        return

    diffs = np.diff(coords, axis=2)
    if dt < 0:
        return
    vels = diffs / dt
    speeds = np.sqrt(vels[:,0,:]**2 + vels[:,1,:]**2)
    avg_speeds = np.mean(speeds, axis=1)
    all_speeds.append(avg_speeds)
    all_times.append(times[-1])

@server.stopfunc
def plot_final_avg_speed(server):
    all_speeds_np = np.array(all_speeds)
    import matplotlib.pyplot as plt #re-import for threading issues
    import matplotlib
    matplotlib.use("Agg")
    for i in range(all_speeds_np.shape[1]):
        plt.plot(all_times, all_speeds_np[:,i], linewidth=0.5, alpha=0.7, label=f"{i}")
        plt.xlabel('Time (s)')
        plt.ylabel('Average speed (px/s)')
        plt.tight_layout()
        plt.legend()
        plt.savefig(f"final-vel-plot-{server.feed_id}.pdf", dpi=300)

# CASSETTE ENDS: DISPLAY_FINAL_VEL_PLOT
```

