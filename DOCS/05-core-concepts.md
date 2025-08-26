# Core concepts

TracktorLive is designed to be minimal and scriptable. Most of the work happens
through small user-defined functions called **cassette functions**, which let
you control what happens during tracking and what gets saved or triggered.

Cassette functions come in three types:


### 🎬 Client Cassette Functions (Basic)

Client cassette functions are the simplest and most common way to interact with
tracking data. They run continuously in the background and receive the latest
buffer of tracking data and timestamps. You can use them to trigger devices,
monitor zones, save values, or drive visualizations.

A typical client cassette looks like this:

```python 
@client 
def log_position(data, clock):
    coords = data[0, :, -1]  # x, y of the most recent frame
    print(f"t = {clock[-1]:.2f}s, x = {coords[0]:.1f}, y = {coords[1]:.1f}")
```

This function is automatically called every few milliseconds as long as the
tracking is active.  There is no guarantee that the server will have processed
another frame by this time, so the client might get the same data over several
iterations. Such an effect is necessary for real-time applications.

To write one:

* Decorate a function with `@client`
* Accept two arguments: `data` and `clock`
* Use the last index `-1` to access the most recent tracked values
* Optional: use previous time points by indexing further back (e.g. `-2`, `-3`)

### Note on Data Shapes

The function `server.get_data_and_clock()` returns two NumPy arrays:

    data: shape (n_ind, 2, buffer_length)

    clock: shape (buffer_length,)

These are also the data and clock accessible to the clients. This means:

-    For 1 individual and a 10-second buffer at 30 fps, data.shape will be (1, 2, 300)

-    The most recent positions are always at `data[:, :, -1]`

-    The clock array holds the corresponding timestamps, latest at `clock[-1]`

If these shapes are confusing, we recommend reading the docs for
[numpy](https://numpy.org).


### 🧩 Server Cassette Functions

Server cassette functions are slightly more advanced and give you direct access
to video frames and state. These are used when you need to:

- Edit video and tracking properties
* Dynamically write video
* Overlay graphics on live frames
* Run tracking-dependent logic directly during processing
- Modify frames prior to processing

```python
@server
def overlay_rectangle(server):
    frame = server.framesbuffer[-1] # Draw semi-transparent overlays or annotate frame
```

To write one:

* Decorate a function with `@server`
* Accept a single `server` argument
* Access `server.framesbuffer[-1]` for the latest *tracked* frame
- Access server.current_frame for the frame about to be submitted to the
  tracking procedure
* Access `server.get_data_and_clock()` for safely retrieving position data
* Can modify flags like `server.keep_video.value = True`

---

### ⏹ Stop Cassette Functions

These are called once at the end of a tracking session. They're useful for
saving final results like:

* Writing out a video clip
* Saving a CSV file
* Closing resources (e.g., files, serial ports)

```python
@server.stopfunc
def save_final_video(server):
    server.dumpvideo("final.avi") #works only if the server was recording!
```

---

### ⏱ Start Cassette Functions

Start cassettes run once, just before tracking begins. You can use them to sync
timers, or log a start event.

```python
@server.startfunc
def announce(server):
    print("Tracking has started.")
```

---

### Internals (Briefly)

Behind the scenes:

* All tracking and cassette execution is multiprocessing-safe
* A shared data buffer and clock are synchronized using a semaphore server
* You don't need to manage threads, timers, or shared memory manually

All you have to do is define functions, decorate them, and run
`trl.run_trsession(...)`.

---

## Writing Your Own Cassette Functions

Cassette functions are the core way to use and customize TracktorLive.
TracktorLive provides flexibility: you can write simple one-liners or build
complete pipelines to control recordings, trigger devices, or annotate frames.

---

### Writing a Client Cassette (Recommended)

Client cassettes are the easiest place to start. They are regular Python
functions that are called automatically every few milliseconds while tracking is
active.

To write one:

1. Spawn a client:

   ```python
   feed_id="your-id-here"
   server = trl.spawn_trserver(
                0,
                params,
                realtime=True) # records from camera.
   # Ensure params is a defined dictionary.

   client = trl.spawn_trclient(feed_id)
   ```

2. Decorate your function with `@client`:

   ```python
   @client
   def print_speed(data, clock):
        curr = data[0, :, -1]
        prev = data[0, :, -2]
        dt = clock[-1] - clock[-2]
        if dt > 0:
            speed = np.linalg.norm(curr - prev) / dt
            print(f"{clock[-1]:.2f}s: speed ={speed:.2f}")
    ```

3. Pass the client to `trl.run_trsession(server, semm, client)`

**Notes**:

* `data` has shape `(n_ind, 2, N)`
* Always check for `np.any(data < 0)` to avoid using invalid frames, where
  tracking couldn't find an individual. When no individuals could be found the
  locations are filled in as (-1, -1).
- You can also use np.any(np.isnan(data)) to avoid untracked times. (At
  initialisation, the buffer is full of NaNs. These get overwritten as tracking
  proceeds.)


### 🎥 Writing a Server Cassette (Advanced)

If you need access to live frames or want to influence recording directly, you
can write a server-side cassette.

Here is an example to begin recording only when the individual moves to the very
left of the screen.

1. Decorate your function with `@server`:


   ```python
   @server
   def monitor(server):
        data, clock = server.get_data_and_clock()
        coords = data[0, :, -1]
        if coords[0] < 100:
            server.keep_video.value = True

   @server.stopfunc
   def end(server):
        server.dumpvideo(outfile="vidout.mp4")
   ```

2. Inside your function:

   - Access current frame about to be tracked with server.current_frame.
   * Access tracked frames with `server.framesbuffer` (list, None when not yet
     tracked)
   * Access tracking data with `server.get_data_and_clock()`
   * Set flags like `keep_video.value`, `write_video.value`, etc.


### ✅ General Advice

* Keep cassette functions short and predictable
* Avoid blocking operations or long sleeps
* Use NumPy and indexing efficiently


## Learning more

TracktorLive includes a set of example scripts that demonstrate common use
cases.  These are a great starting point if you're not sure how to structure
your logic.

You'll find them in the [`examples/`](../examples/) folder on our GitHub
repository.

[previous](04-cli.md) | [next](06-usage.md)
