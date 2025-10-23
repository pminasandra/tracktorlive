---
title: run_command_on_condition
author: Pranav Minasandra
description: Runs a shell command when a function returns True, respecting a time based cooldown rule.
known_issues: None.
---

```python
# CASSETTE BEGINS: RUN_COMMAND_ON_CONDITION
# DESCRIPTION: Runs a shell command when a function returns True, respecting a time
# based cooldown rule.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
RCOC_RUN_COMMAND = "cvlc --fullscreen --play-and-exit --no-osd ./looming-video.mp4"
# Above command is run when the condition is satisfied
RCOC_COMMAND_COOLDOWN = 5 #seconds (if None, no cooldown is imposed)
# Above cooldown is minimum delay between consevutive runs of command

# Example function: is velocity above some threshold?
VEL_CALC_NUM_FRAMES = 5
THRESHOLD_VEL = 125 #px/s
def _vel_higher(data, clock):
    # Extract recent data
    coords = data[0, :, -VEL_CALC_NUM_FRAMES:]  # shape (2, VEL_CALC_NUM_FRAMES)
    times = clock[-VEL_CALC_NUM_FRAMES:]

    # Skip if any coordinates or timestamps are invalid
    if np.isnan(coords).any() or np.isnan(times).any():
        return

    # Compute displacements and distances
    diffs = np.diff(coords, axis=1)  # shape (2, VEL_CALC_NUM_FRAMES-1)
    dists = np.linalg.norm(diffs, axis=0)  # shape (VEL_CALC_NUM_FRAMES-1,)

    dt = times[-1] - times[0]
    if dt > 0:
        avg_speed = np.sum(dists) / dt
    else:
        return

    return avg_speed > THRESHOLD_VEL

RCOC_CHECK_FUNC = _vel_higher #SET TO ANY FUNCTION OF YOUR CHOICE
# FUNCTION SHOULD RETURN True OR False

# INTERNALS: (DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING)
time_last = mp.Value('d', 0.0)
def _cooldown_satisfied():
    if RCOC_COMMAND_COOLDOWN is None:
        return True
    else:
        return time.time() - time_last.value > RCOC_COMMAND_COOLDOWN

def run_quiet_command(cmd=RCOC_RUN_COMMAND):
    """Run a bash command quietly and block until it completes."""
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=os.environ.copy())


@client
def run_command_on_condition(data, clock):
    if RCOC_CHECK_FUNC(data, clock) and _cooldown_satisfied():
        time_last.value = time.time()
        run_quiet_command()

# CASSETTE ENDS: RUN_COMMAND_ON_CONDITION
```
