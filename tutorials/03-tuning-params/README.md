# TracktorLive Tutorial 3: Tuning tracking parameters

Under the hood, TracktorLive runs
[Tracktor](https://doi.org/10.1111/2041-210X.13166)
which uses conventional (non-machine-learning) approaches to track the positions
of objects in a video. However, to perform tracking, Tracktor needs certain
parameter values. TracktorLive comes with a helpful GUI to tune these parameter
values so that tracking can be enabled with minimal guesswork.

## Goal

In this folder is a video, `ant.mp4`, showing the movement of an individual ant
in a petri dish.
You will learn how to generate a .json file containing tracking parameter
values, and you will use these values to track the position of the ant in the
video.

## Method

### Obtaining tracking values

The most important subcommand used here is `tracktorlive gui`. This is the full
command you need to type into the terminal:

```bash
tracktorlive gui --file ant.mp4 --out ant-params.json
```

Now you will see several parameters whose values you can adjust, and a dynamic
display showing the 'contours' of objects seen by Tracktor based on the current
tracking parameters.

<@vivekhsridhar: yeh waala section thoda detail mein bataa dena when you get
time. need some inputs on: har ek parameter karta kya hai, space to pause,
minimise the number of frames with mistakes>

Finally, press the <Esc> key to save parameter values and exit.
You can compare the values you arrive at to the ones we determined for
demonstration purposes, which you can find in the file `supplied-params.json`.

### Tracking the ant

As in [Tutorial 2](../02-tracking-objects/), we will use the `tracktorlive
track` subcommand to track the position of the ant. For this, run:

```bash
tracktorlive track --file ant.mp4 --write-rec ant-params.json
```

### Explanation

![](tracked-ant.jpg)

As you can see. the ant's location has been accurately tracked (plotted above)
most of the time. When TracktorLive cannot detect the position of the ant, it
fills in (x = -1.0, y = -1.0) as the 'unknown' location. In your analyses, you
should drop (or otherwise appropriately handle) these values. Further, at one
point, the ant was mistakenly detected in the top right corner of the frame,
outside the petri plate. Such cases can be avoided by either (a) better tuning
the tracking parameters, or (b) by applying appropriate casettes to minimise
error potential. In the next tutorial, we will explore the tracking of the same
video with the application of such casettes.


