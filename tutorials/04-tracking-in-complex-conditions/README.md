# TracktorLive Tutorial 4: Applying cassettes to improve tracking

In the last tutorial, we used `tracktorlive gui` to tune computer vision
parameters to track the location of an ant in a Petri dish. However, we saw that
the predicted location was erroneous in several instances. The tracking can be
improved by better tuning of parameters and with better lighting. However,
constructing a setup that is optimised for tracking may not always be possible,
either due to specificities of the experimental design or due to costs. In such
cases, tracking can be improved by incorporating some of the pre-defined
cassettes available as part of the TracktorLive python library. Note that while
these cassettes can improve tracking performance, they are no substitute for
a well-designed experimental setup. Here, we use these so called cassettes to
track the ant from [Tutorial 3](../03-tuning-params).



## Goal

To apply cassettes and improve tracking performance. The folder for this
tutorial contains the video `ant.mp4`, showing the movement of an individual ant in
a Petri dish. You will apply a cassette to this video to generate another
video. You will then re-tune the tracking parameters and use the new parameters
to do a proper final tracking of the ant.

## Method

Here are of steps we will follow:

1. We will use the
   [Extract Specified
   Frames](../../Library_Of_Casettes/Extract_Specified_Frames/extract_specified_frames.md)
   cassette to pull out a representative frame from the video as a JPEG
   file.

2. We will use this JPEG file to find the centre and radius of the Petri
   dish in the frame. We will then use the [Add Circular
   Mask](../../Library_Of_Casettes/Add_Circular_Mask/add_circular_mask.md)
   cassette and the
   [Boost
   Contrast](../../Library_Of_Casettes/Boost_Contrast/boost_contrast.md)
   cassettes to add a mask, increase the contrast, and improve tracking efficiency.

3. We will re-tune the tracking parameter values using `tracktorlive gui`.

4. We will use the newly tuned parameters alongside the above mentioned
   cassettes to properly track the ant.

Hence, we begin using TracktorLive as a python library rather than as a command
line tool. Please note that all python scripts running this library have the
following general format.

```python
import json
import tracktorlive as trl

with open("params.json") as jsonf:
    params = json.load(jsonf)
FEED_ID = "trial-feed"

server, semm = trl.spawn_trserver(0, params, feed_id=FEED_ID)

# SERVER CASETTES WILL GO HERE
# THOSE WILL TAKE CARE OF VIDEO PROCESSING ETC

client = trl.spawn_trclient(feed_id=FEED_ID) #optional

# OPTIONALLY:
# CLIENT CASETTES WILL GO HERE
# THOSE WILL TAKE CARE OF RESPONSE DELIVERY

trl.run_trsession(server, semm, client)
```

First, we will create a 'dummy' set of parameter files to begin using
TracktorLive with our video (see Tutorial 1). For this, type `tracktorlive gui
-f ant.mp4 -o dummy-params.json`  in your shell, tweak the parameter values
randomly, and press `<Esc>` to save. If this feels unfamiliar, we recommend
going back to [Tutorial 1](01-recording-video).

Our final tracking pipeline will apply cassettes to mask out every extraneous
detail outside the ant's Petri plate, and will increase the contrast in the
video.
Before that, we will create the file `pre_record.py`. This file will show us
what Tracktor will 'see' after such cassettes have been applied, and allow us to
tune our tracking parameters for this altered video stream. 
`dummy-params.json` is used to launch this Tracktor Server.
We have added the [Extract Specified
   Frames](../../Library_Of_Casettes/Extract_Specified_Frames/extract_specified_frames.md)
cassette to extract the 100th frame of the video. This will help us specify the
parameters for the [Add Circular
   Mask](../../Library_Of_Casettes/Add_Circular_Mask/add_circular_mask.md)
   cassette, so that disturbances outside the Petri plate do not interfere with
   tracking.
We have also used the
   [Boost
   Contrast](../../Library_Of_Casettes/Boost_Contrast/boost_contrast.md)
   cassette.

This python script will generate another video in the pre_record_ant/ directory, which
you can play to see that details outside the Petri plate have been blacked out
and contrast has been boosted.

Manually rename the created video to 'masked_ant.mp4'. Then, we can use the command
`tracktorlive gui -f masked_ant.mp4 -o true-params.json` to accurately tune
the tracking parameters (see [Tutorial 3](../03-tuning-params)).

Finally, we have created the script `track.py`, that uses all cassettes used here
as well as the `write_recordings=True` option, to accurately track the ant.

## Explanation

![](tracked-ant.jpg)

The tracking performance is much improved. This is
because our cassettes have clearly improved the 'visibility' of the ant and our
ability to distinguish it from background noise. Compare the frames with and without our
cassettes below:

![](pre_record_ant_fr_100.jpg)
![](post_cassettes.jpg)

The script `track.py` takes the original, unedited video and applies the cassettes
on to that video feed. Then, with these 'better' frames, it will use the new better tuned
tracking parameters to track the ant.

## Use-case

If your goal is only to track animals, this tutorial is all you need to proceed.
Instead of `ant.mp4`, you can input your camera feed directly into the Tracktor
server in track.py to track in real time, by specifying the camera ID (e.g., 0).
You will also then set the variable `realtime` to `True`.

For tuning the parameters after cassette application, you first need to record
a brief (e.g., 10 min) video from your camera (see [Tutorial 1](../01-recording-video)). Then,
use a script like `pre_record.py` on this short video to apply cassettes and
obtain a new, modifed 10 min video. You will then use `tracktorlive gui` to tune
tracking parameters with this modified video. As long as your setup
remains unchanged, and as long as you apply the same cassettes as in `pre_record.py`, the code in
`track.py` can be changed to work directly with your camera feed, so that you
can track from a live stream for any duration.
