TracktorLive (v0.9-beta)
============

**TracktorLive** is a real-time video tracking and data serving
framework designed for lightweight, scriptable tracking of individual
animals in behavioral experiments. It
provides programmatic hooks for processing and responding to tracked data
on-the-fly, with no interaction needed with actual computer vision code.

The video tracking used in this project emerges from Tracktor::

**Sridhar, V. H., Roche, D. G., & Gingins, S. (2019).**
_Tracktor: Image-based automated tracking of animal movement and behaviour._
Methods in Ecology and Evolution, 10(6), 815–820.
DOI:[10.1111/2041-210X.13166"](https://doi.org/10.1111/2041-210X.13166)

TracktorLive builds on that work, enabling real-time
tracking and response delivery.

------------------------------------------------------------------------

✨ Features
----------

-   Real-time tracking of 1 or more individuals from real-time camera feed or pre-recorded video
    sources
-   Buffered data sharing via shared memory (suitable for high-speed
    use)
-   Modular "cassette" system for on-the-fly processing
-   Built-in support for:
    -   Data streaming to external clients
    -   Live or on-demand video and data recording
-   A number of useful [tutorial scripts](tutorials/) and a growing [library of
    cassettes](Library_Of_Casettes/README.md), through which even novice users
    can quickly create and run scripts.
-   Minimal external dependencies (NumPy, OpenCV, Scikit-Learn etc.)

------------------------------------------------------------------------

🧠 Concept
---------

TracktorLive works on a **server--client model**, where:

-   A **server** processes a video stream and maintains a shared data
    buffer with clock and tracked locations.
-   One or more **clients** can connect and access this data in real
    time.
-   Small, user-defined functions (["cassettes"](./Library_Of_Cassettes/)) can be registered to run
    every frame or at server shutdown.
-   This way, all tracking and multiprocessing happens in the background
    allowing users without computer vision experience to directly get involved
    with such experimental setups.

All interaction is via the use of cassettes. Cassettes are designed to be
readily copied into scripts. New cassettes can be written easily
by anyone with basic knowledge of Python. We also suggest the [TracktorLive
Cassette Maker
GPT](https://chatgpt.com/g/g-696e226d0d048191a9dc03b30cdb5427-tracktorlive-cassette-maker),
an openAI customGPT. However, this is not an official part of the software and
our providing this link must not be seen as an endorsement of this company. The
idea for including a customGPT comes from [Dr. Aiswarya Prasad](https://aiswarya-prasad.github.io/).

------------------------------------------------------------------------

📦 Installation
--------------

TracktorLive is mainly targeted towards Linux-like environments. Windows
users are asked to use Windows Subsystem for Linux (WSL) to use our software.
For running this software on a Linux-like system, you can run

```bash
pip install tracktorlive
```

For usage in other platforms, see [DOCS](./DOCS/).

------------------------------------------------------------------------

🔁 Example: Print current location of animal
---------------------------------------------

```python
import tracktorlive as trl

server, semm = trl.spawn_trserver("video.mp4", params, n_ind=1, buffer_size=1, realtime=False)
client = trl.spawn_trclient(server.feed_id)

@client
def printloc(data, clock):
    pos = data[0,:,-1]
    print(clock[-1], ":", pos)
    

run_trsession(server, semm, client)
```

Here is the basic structure of a TracktorLive script:

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


🧪 Real-world Use Cases
----------------------

We provide eight complete tutorials to demonstrate the capabilities of this
software. See out [list of tutorials](tutorials/README.md) to know more.

While these are the uses we have explored so far, we encourage users to try more things. We have
discussed as potential future applications, e.g., 3D tracking using 3 cameras,
and camera control to select recording device based on individual's location.


📬 Status
--------

TracktorLive is a still an evolving toolkit. APIs may change slightlly. You're
encouraged to adapt parts for your own research or build wrappers that
suit your workflow.

For questions or bugs, feel free to open an issue or reach out directly.
