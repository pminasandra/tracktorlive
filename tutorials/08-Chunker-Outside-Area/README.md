# TracktorLive Tutorial 8: Recording a video based on animal position

This tutorial assumes that you have [installed](../../DOCS/03-installation.md)
TracktorLive correctly, and have your web-cam connected and
[accessible](../../DOCS/COMPORT.md).

## Goal

We will capture video segments only when the animal we are tracking is inside or outside a specific area. 
It is useful when recording animal behaviour for a long time, but we are interested in the behaviour 
happening in specific locations, such as inside a nest or near a food source, etc.

The system monitors position data extracted from video input and
automatically saves short clips to disk when the animal is inside or outside the area of interest. 
This allows for real-time filtering and efficient storage of only behaviourally relevant video. 
In this case, we will record only when the ant is outside the area of interest (e.g. the nest). 

We will assume that your camera is accessed using the `--camera 0`
argument. However, if you have more than one camera connected to your computer
(including the built-in webcam), you might need to use `1` or `2` (or `3` or...)
instead of `0`.

While we used a short video for this tutorial, we ran this script for 2h and we didn't see any 
buffer issues on a mid-range laptop.

## How It Works

1.  A video is analyzed frame by frame using real-time tracking.
2.  A user-defined function periodically checks whether the individual is inside or outside the nest.
4.  When the individual is outside for at least a configurable time threshold, recording is
    enabled. When the individual moves inside the nest, recording stops and the saved frames
    are written to a file.
5.  At the end of the input (if using video), a final check ensures any
    remaining recording is saved.

## Output

Chunks are saved into the `ant-chunked/` directory as individual
video files. Each file corresponds to a brief period spent outside.
In this example, three clips were stored within the 'chunked videos' folder.

## Usage
**Real-time:**
Connect your web-cam, and configure the tracking parameters using (remember to change camera index as needed):

```
tracktorlive gui --camera 4 --out ./p-ant.json
```

This will store the tracking parameters in the p-ant.json file.

Then run:

```
python ant-chunk-tracktorlive.py
```

Remember to modify the camera index as needed in ``` server, semm = trl.spawn_trserver(4, ...) ```.
In some OSs we may need to use ```python3``` instead.
We can adjust the time threshold, area of interest and output directory within the script.

**Video file**
To test this script on the video provided, use:

```
python ant-chunk-tracktorlive-video.py # or python3
```
This script has been modified to analyse the video "ant-video-chunking.mp4" instead of the camera feed.

## Real-World Applications

- Performing more advanced video analyses on chunks can be faster than the
  alternative
- Great for behavioural experiments when we are interested in the behaviour in specific zones.
- This method saves space on disk and decreases the workload of observers (less hours of videos to check).
- We directly obtain the number of exits/enters by counting the number of videos stored. 

## Video example

This video was generated using the script ```ant-chunk-tracktorlive.py```. 

https://github.com/user-attachments/assets/618d2984-faa8-4764-9162-b6e9317dc2a7

