
# General usage instructions

With all this information, you are almost ready to start writing your own custom
scripts using TracktorLive. Overall, this is the set of steps you need to keep
in mind for using this software.

We explain the entire process here considering an example, a video feed coming in from
a webcam that can be accessed with `--camera 0`.


## 0. Set up the basic structure of the code

Your python script will have this overall structure:

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

**See [Tutorials](../tutorials) for
a detailed introduction to the use of command-line utilities, 
python scripts, and cassettes.
**

## 1. Think about how the video will be processed.

Do you want the video to be cropped before tracking?
Do you want contrast enhanced, or certain areas masked?
From our [Library of Cassettes](../Library_Of_Cassettes), you can choose from a
growing number of video processing options. 

## 2. Record a brief video first.

To optimise tracking parameters, first record a short ~10 minute video of the
experimental setup with your camera. You can do this using the `tracktorlive`
command-line utility. You can then apply various server-side cassettes on this
video to obtain a 'processed' video, which corresponds to what the tracking
system 'sees'. Optimise tracking parameters for this processed video using the
`tracktorlive gui` subcommand.

## 3. Use these parameters to run the Tracktor server.

Using the parameter values from step 2, you can begin real-time tracking of the
animals in your setup. This is true as long as the setup remains identical to
the way it was in step 2. You can add different server-side cassettes and change
parameter values of the `trl.spawn_trserver` function to alter the behaviour of
the server. (A detailed description of all possible options can be found in the
[API style reference](07-reference.md))

## 4. Think about response delivery.

Do you want to control other equipment, like doors or food dispensers, in
response to the animals' locations? Do you want to send an e-mail when animals
interact? Or perhaps you want to play an audio or video stimulus in response to
the animals' movement? 
The [Library of Cassettes](../Library_Of_Cassettes) also contains a large number
of 'response' cassettes.

## 5. Add clients and cassettes.

If you do want response delivery as part of your pipeline, spawn a client using
the `trl.spawn_trclient` function (see above). Then attach client-side cassettes
to these clients. Note that for low-latency responses, you may want to spawn
multiple clients, each handling one task.


## 6. Run everything in parallel.

Use the `trl.run_trsession` method to run your server and all your clients in
one go!
