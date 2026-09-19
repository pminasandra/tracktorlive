# Virtual Camera with `v4l2loopback`

This note describes how to create a virtual V4L2 camera on Linux, feed a
prerecorded video into it in real time, and read it using OpenCV.

## 1. Install `v4l2loopback`

On Ubuntu / Pop!\_OS:

``` bash
sudo apt update
sudo apt install v4l2loopback-dkms v4l2loopback-utils
```

Load the kernel module:

``` bash
sudo modprobe v4l2loopback
```

Check that it loaded:

``` bash
lsmod | grep v4l2loopback
```

## 2. Find the virtual camera device

List the available V4L2 devices:

``` bash
v4l2-ctl --list-devices
```

For example:

``` text
Dummy video device (0x0000) (platform:v4l2loopback-000):
    /dev/video2

Chicony USB2.0 Camera:
    /dev/video0
    /dev/video1
```

Here, `/dev/video2` is the virtual camera.

If desired, a particular device number can be requested when loading the
module:

``` bash
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback video_nr=10 card_label="Virtual Camera"
```

This should create `/dev/video10`.

## 3. Feed a prerecorded video into the virtual camera

Using FFmpeg:

``` bash
ffmpeg -re -stream_loop -1 -i your_video.mp4 \
    -f v4l2 -pix_fmt yuv420p /dev/video2
```

Options:

-   `-re` reads the input according to its normal timestamps,
    approximating real-time playback.
-   `-stream_loop -1` loops the video indefinitely.
-   `/dev/video2` is the virtual V4L2 camera device.

Leave this command running while another program reads from the virtual
camera.

## 4. Test with OpenCV

Create a Python script such as `test_camera.py`:

``` python
import cv2

DEVICE = "/dev/video2"

cap = cv2.VideoCapture(DEVICE)

if not cap.isOpened():
    raise RuntimeError(f"Could not open {DEVICE}")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    cv2.imshow("Virtual Camera", frame)

    # Quit with q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

Run the FFmpeg command first, then in another terminal:

``` bash
python test_camera.py
```

The prerecorded video should appear in the OpenCV window as though it
were coming from a camera. Press `q` to quit.

## Notes

The virtual camera can subsequently be opened by software using the
normal V4L2/OpenCV camera interface:

``` python
cv2.VideoCapture("/dev/video2")
```

This makes it possible to repeatedly present the same prerecorded input
to software designed to operate on a live camera feed.
