
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



## 1. Think about how the video will be processed.

Do you want the video to be cropped before tracking h

## TODO:
* explain stuff about server casettes being used to process video before
  tracking
* record video first and then tune param values
* use those param values to set up and run the server
* Think what the client will do
* Add appropriate client casettes
* Done and dusted
