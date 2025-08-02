
# 📚 Cassette Library

Below, we present a library of modular cassettes designed for use with TracktorLive. Each cassette can be utilised independently to perform specific functions or combined seamlessly with others to construct comprehensive Python scripts. This flexible structure enables users to customise and execute a wide range of TracktorLive functionalities according to their experimental or analytical needs.

- [Movement & Position cassettes](#1-movement-and-position-cassettes)
- [Visualisation cassettes](#2-visualisation-cassettes)
- [Video manipulation cassettes](#3-video-manipulation-cassettes)
- [Matrix cassettes](#4-matrix-cassettes)
- [Plotting cassettes](#5-plotting-cassettes)
- [Stop cassettes](#6-stop-cassettes)

# 1. Movement and position cassettes

## 📍 Current position:

This is the most basic and elemental cassette. This cassette is used to detect the current position of an individual, and can be used in real-time or video file examples. This cassette (or similar) is used in most (or all) of the examples provided.

```
@client
def get_position(data, clock):
    coords = data[0, :, -1]
    if not np.isnan(coords).any():
        x, y = coords
        print(f"Position: x = {x:.1f}, y = {y:.1f}")
```

## ➡️ Direction:

This cassette tracks an individual's movement across frames and calculates their direction based on position changes. It updates direction only when the individual moves beyond a set distance threshold to avoid changes of direction due to noise. Useful for behaviour tracking, navigation analysis, or detecting orientation shifts in real time.

```
direction = 10 # number of pixels that the animal needs to move before updating position (avoid noise)
prev = None
@client
def get_angle(data, clock):
    global direction, prev
    if prev is None or np.isnan(prev).any():
        prev=data[0, :, -1]
        return
    else:
        coords = data[0, :, -1]
        Xt=coords[0] - prev[0]
        Yt=coords[1] - prev[1]
        distance = np.sqrt(Xt**2 + Yt**2)
        # if the distance moved is higher than X pixels we update direction and previous position
        if distance > int(direction):
            angle=math.degrees(math.atan2(Yt,Xt)) %360
            prev=data[0, :, -1]
            print(angle)
```

# 2. Visualisation cassettes

## 👀 Visualise video or camera feed on screen:

This code will display the video or camera feed using openCV.

```
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    # copy the frame from the server
    fr = server.framesbuffer[-1].copy()
    cv2.imshow('tracking', fr)

    cv2.waitKey(1)
```

## :black_square_button: Create a mask:

These cassettes create a black image (a mask) with the same dimensions as the video frames. On this mask, we draw a white shape (circular or rectangular) that defines the area we want to keep visible. Finally, we apply this mask to the video frame: all areas outside the shape (black regions) are removed, so only the area inside the defined shape remains visible.

### Circular mask

```
# define position of mask, we define the centre of the circle (relative to the centre of the image)
mask_offset_x = -18
mask_offset_y = -5
# define radius of the circle
radius_mask = 110

@server
def add_mask(server):
    # obtain frame from server
    frame = server.current_frame
    # in case there is no frame
    if frame is None:
        return
    # draw mask
    mask = np.zeros((frame.shape[0], frame.shape[1]))
    cv2.circle(mask, (mask.shape[1]//2 + mask_offset_x, mask.shape[0]//2 + mask_offset_y), radius_mask, 255, -1) # these numbers define the colour intensity and if the mask is filled or not
    frame[mask == 0] = 0
```

### Rectangular mask

```
# Mask area (rectangle)
x1, y1 = 205, 40
x2, y2 = 570, 300

@server
def add_mask(server):
    frame = server.current_frame
    if frame is None:
        return
    #draw rectangular mask on the frame
    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype = np.uint8)
    cv2.rectangle(mask, (x1,y1), (x2,y2), 255, -1) # these numbers define the colour intensity and if the mask is filled or not
    frame[mask == 0] = 0
```

## :clock8: Add timestamp:

### Add timestamp on the GUI video (the one we visualise on real-time)

This cassette adds a timestamp to the video we visualise, but it does not appear in the recorded video. This is useful for real-time tracking, but not for analysing saved videos.
Because the timestamp is added after retrieving the frame, there may be a small error (a few milliseconds) between the displayed time and the actual time the frame was captured.

```
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    # copy the frame from the server
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    # get current time
    now = datetime.now()
    # change format
    data_string = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"
    # add time on the frame we are visualising
    cv2.putText(fr2, data_string, (5, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1) # Here we can change position of the text, font, size and colour
    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)
```

### Add timestamp on recorded videos and/or the GUI video (the one we visualise)

This cassette is useful for chunked videos, or normal recording, and can add the current time on the video files. There may be a small error (a few milliseconds) between the displayed time and the actual time the frame was captured.

```
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    # If we are recording, print timestamp on recorded/chunked videos
    if server.recorded_frames:
        # get frame
        frame = server.recorded_frames[-1]
        # Input time with date, H:M:S on the recorded/chunked videos.
        now = datetime.now() 
        # Change format, we can add information regarding the camera used, the experimental condition, etc.
        data_string = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"
        cv2.putText(frame, data_string, (5, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1) # Here we can change position of the text, font, size and colour
    # Print current time on the gui video 
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy() 
    now = datetime.now()
    # We can add additional information in the video we visualise that will not appear on the recorded video.
    data_string = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"
    cv2.putText(fr2, data_string, (5, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)
    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)
```

### Add experimental time elapsed as a timestamp on recorded videos and/or the GUI video (the one we visualise)

This cassette is useful for both chunked and continuous recordings. It adds a timestamp showing the time elapsed since the beginning of the experiment.  
In this case, the displayed time is accurate, as it is recorded at the exact moment each frame is captured.

```
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    # print timestamp on recorded video (or chunked videos)
    if server.recorded_frames:
        # get frame
        frame = server.recorded_frames[-1]
        # get time from the server (clock)
        now = server.clockbuffer[-1] 
        # change format, we can add information regarding the camera used, the experimental condition, etc.
        data_string = f"{now:.2f}"
        # print on video
        cv2.putText(frame, data_string, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1) # Here we can change position of the text, font, size and colour
    # Here below we can print the time on the gui video. We can print the elapsed time, or the current time (we can display additional information that will not appear in the recorded videos):
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    # 1. uncomment this section below to print current time:
    # ~ now = datetime.now()
    # ~ data_string = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"
    # 2. uncomment this section below to print elapsed time:
    now = server.clockbuffer[-1] 
    data_string = f"{now:.2f}"
    # Here below will add a timestamp (according to the what we chose above) to the video we visualise
    cv2.putText(fr2, data_string, (5, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)
    
    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)
```

## 🎯 Region of Interest:
These cassettes are used to define regions of interest (ROI). These regions can be combined with the visualisation cassettes, to highlight specific zones in videos, or could be used in real-time experiments to trigger actions when animals are inside or outside those ROI.

### Rectangular ROI

```
# Define area of interest (rectangular)
# Edges of the area in pixels
top = 120
right = 300
bottom = 350
left = 150

# Choose colour and transparency factor
color = (0, 255, 0)  # Green
alpha = 0.5  # Transparency factor: 0.0 = fully transparent, 1.0 = fully opaque

# Coordinates
top_left = (left, top)
bottom_right = (right, bottom)

# Display the region of interest on screen (this is not visible in recorded videos; to do so please combine with other cassettes: e.g. take a look at timestamp cassettes)
# Draw rectangle on the overlay
@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    #rectangle
    cv2.rectangle(fr, top_left, bottom_right, color, thickness=-1)
    # Blend the rectangle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)

    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)
```
### Detect individuals inside/outside a rectangular region of interest
This cassette can be used after the cassette above (Rectangular ROI) to detect when individuals are inside or outside the ROI.  
For example:
- To trigger an event when all individuals are inside the ROI  
- To monitor entries and exits for behavioural analysis  
- To send a signal to external hardware (e.g. Arduino) when crossing the ROI boundary
```
def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
    return left < locs[0] < right and top < locs[1] < bottom
    
# In this example, we check if the individual has crossed the right edge.
# Only the X position is considered; the Y position is ignored.

def _out_rect(locs, right=right):
    return locs[0,0] > right

# The _in_rect and _out_rect functions can be used to trigger Arduino actions, start or stop recording (chunk videos), looming, etc.
```

### Circular ROI

```
# Define region of interest (circle)
# parameters
center = (268, 167)  # Centre of the circle
radius = 45          # Radius of the circle
color = (0, 255, 0)  # Green
alpha = 0.5          # Transparency factor

# Draw circle on the overlay

@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    # Draw filled circle on fr
    cv2.circle(fr, center, radius, color, thickness=-1)
    # Blend the circle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)

    cv2.imshow('tracking', fr2)

    cv2.waitKey(1)
```
### Detect invididuals inside/outside the circular region of interest

This cassette can be used after the cassette above (Circular ROI) to detect when individuals are inside or outside the ROI.  
For example:
- To trigger an event when all individuals are inside the ROI  
- To monitor entries and exits for behavioural analysis  
- To send a signal to external hardware (e.g. Arduino) when crossing the ROI boundary
```
def _in_circle(locs, center=center, radius=radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

# The _in_circle function can be used to trigger Arduino actions, start or stop recording (chunk videos), looming, etc.
```

# 3. Video manipulation cassettes

## ✂️ Chunking:

These cassettes help to record videos only when individuals are inside or outside of specific regions of interest.
They can be combined with "region of interest" and "visualisation" cassettes.

### Individual inside or outside of a region of interest

Here below we provide an example to record the video only when the individual tracked is in the right half of the setup. 
This means that we start recording when the individual crosses the right edge of our region of interest.
First, we need to define a ROI with a cassette, for instance:

```
# Define right edge of the ROI (pixel):
right = 300

# Function to detect when the individual is outside of the ROI
def _out_rect(locs, right=right):
    return locs[0,0] > right
    
# We could also define a circular region of interest, and then check when locs[0, 0] > than desired distance (to record when individual is outside the area).
```
After that, we can use the chunking cassette, such as:
```
# Function to do the chunking based on the condition above:
# Global variables needed to track the time spent inside or outside the regions of interest
frames_outside_thresh = 0
MIN_FRAMES_OUTSIDE = 30  # minimum frames animal must be outside to start recording

frames_inside_thresh = 0
MIN_FRAMES_INSIDE = 30  # minimum frames animal must be inside to stop recording

@server
def chunking(server):
    global frames_outside_thresh, frames_inside_thresh
    data, _ = server.get_data_and_clock()
    curr_vals = data[:,:,-1]
    prev_vals = data[:,:,-2]
    # if unknown location
    if np.any(curr_vals < 0.0):
        return None
    # if animal just moved out of the rectangle
    if _out_rect(curr_vals):
        frames_inside_thresh = 0  # reset inside counter
        frames_outside_thresh += 1 # count frames spent outside, and if higher than threshold, start recording
        if frames_outside_thresh >= MIN_FRAMES_OUTSIDE: 
            if len(server.recorded_frames) == 0:
                server.keep_video.value = True
                print("recording in progress...")
    # if animal is inside the area:
    else:
        # in case we are recording, we count the frames spent inside and stop recording when this number is larger than the threshold
        if len(server.recorded_frames) > 0:
            frames_inside_thresh += 1
            if frames_inside_thresh >= MIN_FRAMES_INSIDE:
                server.keep_video.value = False
                frames_outside_thresh = 0  # reset after dump
                frames_inside_thresh = 0  # reset after dump
                # define video names
                fname = f'chunk-{ulid.ULID()}.avi'
                server.dumpvideo(joinpath('ant-chunked', fname))
```

### Record when two animals are close to each other

This cassette will record only when to animals are in close proximity. 

```
# We want to record when animals are within this distance in pixels:
THRESH_APPROACH_DIST = 60 #px
THRESH_APPROACH_DIST2 = THRESH_APPROACH_DIST**2 #px**2

# Function to do the chunking based on this distance:
# Global variable to track how long animals have been apart
# This is important to avoid recording very short videos due to noise, or sporadic errors during recordings.
# If individuals are difficult to track, and you observe that sometimes one individual is not detected, it is adviced to add the following rule: "if individuals are too close, less than X, do not record", this will avoid recording when one individual identity is lost.

frames_outside_thresh = 0
MIN_FRAMES_OUTSIDE = 30  # minimum frames animals must be apart to stop recording

frames_inside_thresh = 0
MIN_FRAMES_INSIDE = 30  # minimum frames animals must nearby to start recording

@server
def chunking(server):
    global frames_outside_thresh, frames_inside_thresh
    data, _ = server.get_data_and_clock()
    curr_vals = data[:,:,-1]

    if np.any(curr_vals < 0.0):
        # unknown location
        return None
    # Compute distance between individuals
    dist2 = ((curr_vals[0,:] - curr_vals[1,:])**2).sum()
    
    # if they are close to each other:
    if dist2 <= THRESH_APPROACH_DIST2:
        frames_outside_thresh = 0  # reset counter: they're close
        frames_inside_thresh += 1
        # How long have they been in close proximity:
        if frames_inside_thresh >= MIN_FRAMES_INSIDE: 
            if len(server.recorded_frames) == 0:
                server.keep_video.value = True
                print("recording in progress...")
    # if individuals are not close to each other, we check the time spent apart, and we stop recording.
    else:
        if len(server.recorded_frames) > 0:
            frames_outside_thresh += 1
            if frames_outside_thresh >= MIN_FRAMES_OUTSIDE:
                server.keep_video.value = False
                frames_outside_thresh = 0  # reset after dump
                frames_inside_thresh = 0  # reset after dump
                # name file
                fname = f'chunk-{ulid.ULID()}.avi'
                server.dumpvideo(joinpath(directory_name, fname))
```
## 🔍 Crop & Register:

This cassette crops zoomed images of the individuals detected.
First, we can add a cassette to display the video or camera feed:
```
# 1. Add cassette to show video, such as:
@server
def show(server):
    fr = server.framesbuffer[-1]
    if fr is None:
        return
    cv2.imshow('tracking', fr)
    cv2.waitKey(1)
```

Then, we can add our crop & register cassette, such as:

```
# Define parameters
CROP_WIDTH, CROP_HEIGHT = 200, 200
CROPPED_DIR = "centered-clips"
os.makedirs(CROPPED_DIR, exist_ok=True)

# 2. We define a crop to center function:
@server
def crop_to_center(server):
    data, _ = server.get_data_and_clock()
    pos = data[4, :, -1]

    if np.any(np.isnan(pos)):
        return

    if np.any(pos < 0):
        return

    x, y = int(pos[0]), int(pos[1])
    frame = server.framesbuffer[-1]
    if frame is None:
        return
    h, w = frame.shape[:2]

    x1 = max(x - CROP_WIDTH // 2, 0)
    y1 = max(y - CROP_HEIGHT // 2, 0)
    x2 = min(x1 + CROP_WIDTH, w)
    y2 = min(y1 + CROP_HEIGHT, h)
    x1 = max(x2 - CROP_WIDTH, 0)
    y1 = max(y2 - CROP_HEIGHT, 0)

    crop = frame[y1:y2, x1:x2]
    if crop.shape[:2] != (CROP_HEIGHT, CROP_WIDTH):
        return

    if not hasattr(server, "crop_writer") or server.crop_writer is None:
        outpath = joinpath(CROPPED_DIR, f"centered-{server.feed_id}.avi")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        server.crop_writer = cv2.VideoWriter(outpath, fourcc, server.fps, (CROP_WIDTH, CROP_HEIGHT))

    server.crop_writer.write(crop)
```
We should add a stop cassette at the end (see description below):
```
# Stop function
@server.stopfunc
def close_crop_writer(server):
    if hasattr(server, "crop_writer") and server.crop_writer is not None:
        server.crop_writer.release()
        server.crop_writer = None
```

# 4. Matrix cassettes

## 🎮 Looming:

This cassette shows how to setup a server-client system to run a specific command, in this case play a video, whenever the animal is moving. 
The video example is motivated by presenting looming stimuli, but any shell command can be added in its place, e.g., to run equipment, launch web services, etc. 
Likewise, any condition other than velocity can also be programmed.

```
# User params:
VEL_CALC_NUM_FRAMES = 5
THRESHOLD_VEL = 125 #px/s
RUN_COMMAND = "cvlc --fullscreen --play-and-exit --no-osd ./looming-video.mp4"
COMMAND_COOLDOWN = 15 #seconds
# Code starts below.

# Uncomment this code below to show the video on screen:
# ~ @server
# ~ def show(server):
    # ~ if server.current_frame is None:
        # ~ return
    # ~ cv2.imshow('tracking', server.current_frame)
    # ~ cv2.waitKey(1)

client = trl.spawn_trclient(server.feed_id)

time_last = mp.Value('d', 0.0)

## We will now write a function to do the velocity based video response on this distance:
@client # adding this decorator makes this a client-side casette
def average_speed(data, clock):
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

    if avg_speed > THRESHOLD_VEL and time.time() - time_last.value > COMMAND_COOLDOWN:
        time_last.value = time.time()
        run_quiet_command()
```

## 🤖 Arduino:

These cassettes are useful to connect real-time behaviour with actions triggered by an Arduino board, or similar devices.

### Detect the Arduino port
This cassette is used to automatically detect the USB port connected to the Arduino.
This code has been tested on Linux, macOS, and Windows. However, some systems may use different port naming conventions, which might require adjusting the code.

```
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        manu = (port.manufacturer or "").lower()
        if 'ttyUSB' in port.device or 'ser' in desc or 'arduino' in manu or 'arduino' in desc:
            return port.device
    raise RuntimeError('No arduino device could be found')
```
To run this cassette, and verify that the Arduino port is well detected, we can run: 

```
port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)
```
The ```ser``` line establishes a serial connection between your computer and the Arduino via the specified port.

### Tracking several animals + ROI

This cassette will send a signal to the Arduino board when all individuals tracked are inside a specific ROI.
This code can be easily modified to trigger an action in case ANY animal is in the region of interest instead of ALL of them.
This cassette should be combined with Detect Arduino port, region of interest and visualise cassettes.

Before using this cassette, we should add some cassettes described above:

```
#1. Add cassette to Detect Arduino port here (def find_arduino_port()).

# We test if we can detect the arduino port correctly and establish connection:
port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)

# 2. Insert a region of interest (ROI) cassette here

# 3. Define a function using this ROI, such as _in_circle() or _in_rect(), to detect if individual is inside or outside of the ROI.

# 4. Insert a cassette to draw your region of interest on the overlay here (optional).
```

Once the region of interest (ROI) is defined, and the connection to the Arduino is established, we launch the client function.
```
# This function tracks individuals and sends a signal to the Arduino board when all individuals are inside the ROI.
# In this example, the Arduino opens a door when all individuals are inside the ROI.
# The door closes approximately one second later (30 frames) once any individual leaves the ROI.
# The specific action performed by the Arduino must be programmed on the Arduino board itself.
# See our Arduino code examples for guidance.

# Indicates whether the door is open or close.
door_open = False
# Global variables used.
lastTrigger = 0
count = 0 

@client
def send_to_arduino_open(data, clock):
    global door_open, lastTrigger, count
    curr_loc = data[:,:,-1] #get last location
    all_in = all(_in_rect(ant) for ant in curr_loc) # who is in the ROI?
    now = time.time() # get current time to count the time elapsed between actions.
    if all_in and not door_open and now - lastTrigger > 5:# animal just moved into the rectangle, and five seconds have elapsed since last time the door was activated
        ser.write(b'm')
        print("pillbugs in the house")
        door_open = True
        lastTrigger = time.time()
    
    elif not all_in and door_open and now-lastTrigger > 5:
        count += 1
        if count > 30: #we wait some time before moving the door
            ser.write(b'k')
            print("pillbugs out")
            door_open = False
            lastTrigger = time.time()
            count = 0
```

### Tracking a single animal + ROI

This cassette is useful for sending a signal to the Arduino board when an individual enters or exits a Region of Interest (ROI).
It is recommended to add a threshold time — the minimum amount of time the individual must remain inside or outside the ROI before the signal is sent — to avoid false triggers from brief movements or noise.
Before running this cassette, we should run some cassettes described above:

```
#1. Add cassette to Detect Arduino port here (def find_arduino_port()).

# We test if we can detect the arduino port correctly and establish connection:
port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)

# 2. Insert a region of interest (ROI) cassette, and Define a function using this ROI here. For instance:

center = (268, 167)  # Centre of the circle
radius = 45          # Radius of the circle
color = (0, 255, 0)  # Green
alpha = 0.5          # Transparency factor

def _in_circle(locs, center=center, radius=radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

# 3. Insert a cassette to draw your region of interest on the overlay here (optional).
```

Once the region of interest (ROI) is defined, and the connection to the Arduino is established, we launch the client function.

```
# This function tracks our individual and sends a signal to the Arduino board the individual is inside the ROI.
# The specific action performed by the Arduino must be programmed on the Arduino board itself.
# See our Arduino code examples for guidance.

@client
def send_to_arduino(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]

    if _in_circle(curr_loc) and not _in_circle(prev_loc):# animal just moved into the circular area
           ser.write(b'm')
```


# 5. Plotting cassettes
 
## 📈 Automatically generate and update plots:

### Automtaically generate a plot at the end of a video file

This cassette displays and saves a plot when we reach the end of the video file we are analysing. In this example, we compute the individual speed (pixels/second) every five frames.

```
# Shared buffer
all_speeds = []
all_times = []
# User params:
VEL_CALC_NUM_FRAMES = 5

@server
def average_speed(server):
    global all_speeds, all_times
    data, clock = server.get_data_and_clock()
    coords = data[0, :, -VEL_CALC_NUM_FRAMES:]
    times = clock[-VEL_CALC_NUM_FRAMES:]

    if np.isnan(coords).any() or np.isnan(times).any():
        return

    diffs = np.diff(coords, axis=1)
    dists = np.linalg.norm(diffs, axis=0)
    dt = times[-1] - times[0]
    if dt > 0:
        avg_speed = np.sum(dists) / dt
        all_speeds.append(avg_speed)
        all_times.append(times[-1])
    else:
        all_speeds.append(0)
        all_times.append(times[-1])
        
@server.stopfunc
def plot_final_avg_speed(server):
    plt.scatter(all_times, all_speeds, s=8)
    plt.xlabel('Time (s)')
    plt.ylabel('Average speed (px/s)')
    plt.tight_layout()
    plt.savefig('./ex1_fig1a.eps', format='eps', dpi=300)
    plt.show()
```

### Display and update a plot in real-time:

This cassette displays (and saves) a plot every few seconds. It is useful for monitoring a variable in real time—allowing you to stop an experiment when, for example, an individual’s value reaches a certain threshold.

While it is tailored for use with a real-time video feed, it can also be applied to pre-recorded video files.

In this example, we compute individual speed (in pixels per second) every five frames, and update the plot display every two seconds. The last displayed plot is automatically saved.

```
client = trl.spawn_trclient("update_plot")

# Shared buffer
all_speeds = []
all_times = []
# User params:
VEL_CALC_NUM_FRAMES = 5
checkpoints = 2 # in seconds

@client
def average_speed(data, clock):
    global all_speeds, all_times
    coords = data[0, :, -VEL_CALC_NUM_FRAMES:]
    times = clock[-VEL_CALC_NUM_FRAMES:]

    if np.isnan(coords).any() or np.isnan(times).any():
        return

    diffs = np.diff(coords, axis=1)
    dists = np.linalg.norm(diffs, axis=0)
    dt = times[-1] - times[0]
    if dt > 0:
        avg_speed = np.sum(dists) / dt
        all_speeds.append(avg_speed)
        all_times.append(times[-1])
    else:
        all_speeds.append(0)
        all_times.append(times[-1])
    plt.ion()
    if int(times[-1]) % checkpoints == 0:
        plt.clf()
        plt.scatter(all_times, all_speeds, s=8)
        plt.xlabel('Time (s)')
        plt.ylabel('Average speed (px/s)')
        plt.tight_layout()
        plt.savefig('./ex1_fig1a.eps', format='eps', dpi=300)
        plt.pause(0.001)
```

# 6. Stop cassettes

## 🛑 Stop server functions
Stop cassettes can be use to stop a function or perform an action at the end of a video file, or when stopping a recording. It is useful mostly when analysing a video, to stop all processes when we reach the last frame of the file. 
It can also be useful to stop all processes in real-time experiments after a certain amount of time elapsed, when some specific action was triggered, etc. 

```
# Stop function
@server.stopfunc
def close_crop_writer(server):
    if hasattr(server, "crop_writer") and server.crop_writer is not None:
        server.crop_writer.release()
        server.crop_writer = None
```

```
@server.stopfunc
def stop(server):
    print("Shutting down...")
```

# Missing cassettes : 

## Image manipulation, such as changing light contrast, etc
