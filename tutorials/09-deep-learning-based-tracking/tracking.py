import cv2
from ultralytics import YOLO

import numpy as np
import time
import tracktorlive as trl
import json

VIDEO = "toys.avi"
PARAMS = "toys-params.json"
model = YOLO("yolo11s.pt")
ball_class = next(i for i, name in model.names.items() if name == "sports ball")


# Setting up tracktorlive server
with open(PARAMS) as jsonf:
    params = json.load(jsonf)

server, semm = trl.spawn_trserver(VIDEO,
                            params,
                            n_ind=1,
                            buffer_size=0.3,
                            feed_id="Ball tracker",
                            draw=True,
                            internal_tracking=False,
                            realtime=False,
                            write_video=True)

TOP_LEFT = (1200, 180)
BOTTOM_RIGHT = (1450, 320)

# CASSETTE BEGINS: ZONE_ALERT_OVERLAY
# DESCRIPTION: Draws a black warning box with a red "!" when any tracked object
# is inside the specified rectangular zone.
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES:
zone_alert_TOP_LEFT = TOP_LEFT       # (x, y)
zone_alert_BOTTOM_RIGHT = BOTTOM_RIGHT  # (x, y)

# INTERNALS:
zone_alert_BOX_TOP_LEFT = (135, 135)
zone_alert_BOX_BOTTOM_RIGHT = (335, 335)

@server.atstart
def zone_alert_overlay_begin(server):
    server.not_in_area = True

@server
def zone_alert_overlay(server):
    zone_alert_frame = server.current_frame
    if zone_alert_frame is None:
        return

    zone_alert_data, _ = server.get_data_and_clock()
    zone_alert_positions = zone_alert_data[:, :, -1]

    zone_alert_left, zone_alert_top = zone_alert_TOP_LEFT
    zone_alert_right, zone_alert_bottom = zone_alert_BOTTOM_RIGHT

    zone_alert_active = any(
        not np.isnan(zone_alert_x)
        and not np.isnan(zone_alert_y)
        and zone_alert_x >= 0
        and zone_alert_y >= 0
        and zone_alert_left <= zone_alert_x <= zone_alert_right
        and zone_alert_top <= zone_alert_y <= zone_alert_bottom
        for zone_alert_x, zone_alert_y in zone_alert_positions
    )

    if not zone_alert_active:
        return

    server.not_in_area = False
    cv2.rectangle(
        zone_alert_frame,
        zone_alert_BOX_TOP_LEFT,
        zone_alert_BOX_BOTTOM_RIGHT,
        (0, 0, 0),
        thickness=-1,
    )

    cv2.putText(
        zone_alert_frame,
        "!",
        (195, 310),
        cv2.FONT_HERSHEY_SIMPLEX,
        6.4,
        (0, 0, 255),
        thickness=8,
        lineType=cv2.LINE_AA,
    )
# CASSETTE ENDS: ZONE_ALERT_OVERLAY


# CASSETTE BEGINS: DRAW_ZONE_RECTANGLE
# DESCRIPTION: Draws a translucent rectangle on the frame before tracking.
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES:
DRAW_ZONE_RECTANGLE_ALPHA = 0.4
# Uses existing TOP_LEFT and BOTTOM_RIGHT tuples.
# KNOWN ISSUES: None

@server
def draw_zone_rectangle(server):
    col = (0, 255, 0) if server.not_in_area else (0, 0, 255)
    draw_zone_rectangle_overlay = server.current_frame.copy()

    cv2.rectangle(
        draw_zone_rectangle_overlay,
        TOP_LEFT,
        BOTTOM_RIGHT,
        col,
        thickness=-1
    )

    cv2.addWeighted(
        draw_zone_rectangle_overlay,
        DRAW_ZONE_RECTANGLE_ALPHA,
        server.current_frame,
        1.0 - DRAW_ZONE_RECTANGLE_ALPHA,
        0,
        dst=server.current_frame
    )

# CASSETTE ENDS: DRAW_ZONE_RECTANGLE


# CASSETTE BEGINS: YOLO_TRACKING_SINGLE_OBJECT
# DESCRIPTION: !!CORE TRACKER!! Replaces Tracktor tracking with YOLO and ByteTracker
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES:
model = YOLO("yolo11s.pt")

# INTERNALS:
ball_class = next(i for i, name in model.names.items() if name == "sports ball")
@server
def yolo_tracking(server):

    result = model.track(
        server.current_frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[ball_class],
        conf=0.05,
        imgsz=1280,
        verbose=False,
    )[0]

    cx, cy = -1, -1
    if result.boxes:
        for box in result.boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = box
            w, h = x2 - x1, y2 - y1
            if w < 100 or h < 100:
                continue
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            if server.draw:
                cv2.circle(server.current_frame, (cx, cy), 20, (255, 0, 0), -1)
    server.semaphore.acquire()

    databuffer = server.databuffer
    clockbuffer = server.clockbuffer

    databuffer[:,:,:-1] = databuffer[:,:,1:]
    clockbuffer[:-1] = clockbuffer[1:]

    if server.vid_source_type == "cam":
        clockbuffer[-1] = time.time() - server.t_init
    else:
        clockbuffer[-1] = server.frame_index/server.fps

    databuffer[:,:,-1] = -1.0
    databuffer[:,:,-1] = [cx, cy]
    server.framesbuffer[:-1] = server.framesbuffer[1:]
    server.framesbuffer[-1] = server.current_frame.copy()

    if server.keep_video.value:
        if len(server.recorded_frames) == 0:
            server.recorded_frames.extend(
                    [fr for fr in server.framesbuffer if fr is not None]
                )
        else:
            server.recorded_frames.append(server.current_frame)

    if server.keep_recordings.value:
        if len(server.recorded_points) == 0:
            server.recorded_points.extend(list(server.databuffer))
            server.recorded_times.extend(list(server.clockbuffer))
        else:
            server.recorded_points.append(server.databuffer[:,:,-1])
            server.recorded_times.append(server.clockbuffer[-1])


    if server.write_video.value:
        server.vidout.write(server.current_frame)

    if server.write_recordings.value:
        entry=[clockbuffer[-1]]
        entry.extend(list(databuffer.copy()[:,:,-1].reshape(2*server.n_ind)))
        entry=[str(x) for x in entry]
        print(",".join(entry), file=server.recout, flush=True)
    server.semaphore.release()
# CASSETTE ENDS: YOLO_TRACKING_SINGLE_OBJECT

trl.run_trsession(server, semm)
