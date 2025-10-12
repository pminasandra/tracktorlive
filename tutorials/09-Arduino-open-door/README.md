# TracktorLive Tutorial 9: Activate Arduino with several individuals

This tutorial assumes that you have [installed](../../DOCS/03-installation.md)
TracktorLive correctly, and have your web-cam connected and
[accessible](../../DOCS/COMPORT.md).

## Goal

We will trigger a stepper motor when all animals (two pillbugs) are inside our region of interest (ROI). 
This stepper motor opens a door that provides access to a resource (e.g. food or water).

 and
automatically triggers the Arduino board to open or close the door

We will assume that your camera is accessed using the `--camera 0`
argument. However, if you have more than one camera connected to your computer
(including the built-in webcam), you might need to use `1` or `2` (or `3` or...)
instead of `0`.

While we used a short video for this tutorial, we run this script for 2h and we didn't see any 
buffer issues on a mid-range laptop.

## How It Works

1.  The system monitors position data extracted from camera feed.
2.  A user-defined function periodically checks whether individuals are inside or outside the ROI.
4.  When both individual are inside the ROI the door opens using Arduino.
5.  When one of the individuals moves outside the ROI, after a configurable time threshold, the door closes.


## Run
``` python open-close-door.py```

In the video below, we can see that with this code the setup behaves as intended: the door opens every time 
both individuals are inside the green ROI, but closes when one individual is outside.

## Output

https://github.com/user-attachments/assets/009591e2-2d35-4dc5-a173-55abe1ab010a


