# TracktorLive Overview

Many real-world situations require a setup where a video stream is continually
monitored, objects within that stream are tracked, and when certain conditions
are reached, a response is delivered.  We mainly focus on animal behaviour
experiments. For instance, a mouse is being tracked, and whenever it reaches a particular
set of coordinates, a door is opened. More complex cases might exist, and in
a lot of those cases, a software library to automate such tasks becomes
necessary. This is because:

1. Designing experiments where humans respond to video feeds is expensive and
   laborious, and human speed becomes limited when dealing with a high number of
   tracked individuals. Moreover, human responses come with individual-specific
   biases.
   
2. While it is possible to hard code these tasks, a speed-limit is reached by
   the often separate tasks of object-tracking (e.g., where is the mouse) and
   response delivery (e.g., what do we do with this information about the
   mouse's location?) Since most tracking tasks are largely similar, we could run the
   tracking code in a separate concurrent process. This concurrency provides
   a large speed benefit.

3. Finally, computer vision and object tracking are not aspects of programming
   familiar to most beginners. It would make the learning curve for these tasks
   much less steep if the 'boilerplate' of object tracking happened in the
   background while users only focussed on the response delivery aspect.

TracktorLive is a lightweight, real-time tracking and data streaming framework
designed for use in behavioural experiments, multi-agent video analysis, and
low-latency response delivery. It builds on the original [Tracktor](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.13166) tracking
approach by extending it into a modular, scriptable architecture that supports
real-time computation and flexible output control.
TracktorLive is a full python library, and so its applications are many.

At its core, TracktorLive:

-    Tracks one or more individuals from a live camera or video file

-   Maintains a buffer of recent tracking data in shared memory

-    Serves data to external clients over a simple shared-memory
    interface

-    Allows user-defined functions to process or respond to this data
    frame-by-frame, including modification of server parameters for advanced
    users.

The system is designed to be highly adaptable: we provide examples where you can 
send a message to get stimulus delivery on an Arduino, 
trigger recordings based
on spatial locations of individuals, extract centred video segments, write
custom log files, or launch other local processes.

TracktorLive runs on Unix-like environments (Linux, macOS, WSL in
Windows). A GUI allows users to easily set optimal tracking
parameters and save them as a .json file, which is useful for analyzing multiple
videos using the same experimental setup. Additional parameters to specify the
number of individuals to be tracked, whether the tracking is live or from a
recorded video, where to save output files, are specified in a .py python script.
This .py file also contains server and client cassettes allowing the user to
customize tracking to their specific needs. Basically, only three files are needed to run
TracktorLive: a video file, a .json file with tracking parameters, and a .py file
with the python script to run TracktorLive and customize tracking as needed.
Several examples are available out-of-the box and the .py files for these
examples can be modified by users to suit their needs.

You can use TracktorLive entirely through helper functions and decorators
without worrying about the internals of the multiprocessing and tracking setup.
The end-user can rely on the TracktorLive internals for all that.

[previous]() | [next](02-quickstart.md)
