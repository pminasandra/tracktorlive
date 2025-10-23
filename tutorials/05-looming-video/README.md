# TracktorLive Tutorial 5: Response delivery

In the previous four tutorials we went over the process of getting TracktorLive
to recognise and track your animals. However, responding to animals' positions
in real time is the key purpose of TracktorLive. That's what the 'Live' refers
to, after all. In this tutorial, we will show how to present a simple looming
stimulus as a response whenever a fish in a tank exceeds a certain velocity.

## Goal

In this folder is a video, `flume_video.mp4`, showing the movement of an individual fish
in a rectangular tank.
We will create a python script that takes uses TracktorLive to play
a full-screen video whenever the fish moves over a certain velocity.

![Looming video](looming.gif)
(The above video is to be played only once each time the fish triggers it,
although here on GitHub it will loop endlessly)

## Method

We have already tuned the tracking parameters and saved them in
`flume-video-params.json`. The python script `looming.py` has been written,
which makes use of the
[Run Command On Condition](../../Library_Of_Casettes/Run_Command_On_Condition/run_command_on_condition.md)
cassette to play the video in full-screen. This cassette has been set up, in
this script, to use VLC to set up and play the looming video.

## Explanation

The Run Command On Condition cassette is a _client_ cassette, and is designed
for response delivery. It takes a condition function as a user-defined parameter, and
whenever the function returns 'True', it runs a user-specified shell command.
The function we provided this cassette here was:

```python
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
```

This uses the last 5 frames to compute the average velocity of the individual.
If the average velocity exceeds 125 px / s, it launches a bash command. The bash
command specified by us was:

```bash
cvlc --fullscreen --play-and-exit --no-osd ./looming-video.mp4
```

The above command launches `looming-video.mp4` in full-screen, and exits after
the video finishes. 

## Use-cases

With appropriately specified conditions and commands, you can practically design
a simple system that can do anything. bash commands can be easily used to turn
on and off equipment, transmit data, perform hardware operations, or deliver
notifications or e-mails in specific formats. With some creativity, this
cassette and script can be used in a variety of situations.



