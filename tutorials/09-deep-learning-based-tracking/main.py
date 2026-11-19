import json
import tracktorlive as trl
import cv2
import numpy as np

with open("params-lowres.json") as jsonf:
    params = json.load(jsonf)
FEED_ID = "YOLO-demo"

server, semm = trl.spawn_trserver("sample-lowres.mp4", params, feed_id=FEED_ID, n_ind=5,
                            realtime=False, internal_tracking=False, buffer_size=1)



# CASSETTE BEGINS: YOLO_SERVER_TRACKING
# DESCRIPTION: Replaces Tracktor-based internal tracking with YOLO (given a .pt file),
#   which increases latency but can lead to far better detections. Interpolation used
#   when objects are missing for short periods.
# AUTHOR: TracktorLive Cassette Maker GPT (GPT-6.1-Astra, verified by Pranav Minasandra)
# USER DEFINED VARIABLES:
YOLO_TRL_WEIGHTS = "YOLO_Barn.pt"
YOLO_TRL_CLASSES = None       # e.g. [0] to track only class 0
YOLO_TRL_CONF = 0.25
YOLO_TRL_GATE_PX = None       # optional maximum one-frame prediction error in pixels
YOLO_TRL_CONF_PX = 8.0        # confidence penalty in equivalent pixels
YOLO_TRL_DEVICE = "cuda:0"    # Either "CPU" or "cuda" or "cuda:i" where i is GPU number

import time as yolo_trl_time
import cv2 as yolo_trl_cv
import numpy as yolo_trl_np
from scipy.optimize import linear_sum_assignment as yolo_trl_hungarian
# KNOWN ISSUES: None

@server.startfunc
def yolo_trl_start(server):
    from ultralytics import YOLO
    from pathlib import Path

    weights = Path(YOLO_TRL_WEIGHTS).expanduser()
    if not weights.is_file():
        raise FileNotFoundError(weights)
    server.yolo_trl_model = YOLO(str(weights))
    server.internal_tracking = False
    server.yolo_trl_pos = yolo_trl_np.full((server.n_ind, 2), yolo_trl_np.nan)
    server.yolo_trl_vel = yolo_trl_np.zeros((server.n_ind, 2))
    server.yolo_trl_seen = yolo_trl_np.full(server.n_ind, -1, dtype=int)
    server.yolo_trl_step = 0
    # Native tracking runs after every ordinary per-frame cassette.
    name = yolo_trl_frame.__name__
    server.casettes[name] = server.casettes.pop(name)


def yolo_trl_assign(server, centers, conf):
    np = yolo_trl_np
    pos, vel = server.yolo_trl_pos, server.yolo_trl_vel
    seen, step = server.yolo_trl_seen, server.yolo_trl_step
    server.yolo_trl_step += 1
    points = np.full_like(pos, -1.0)
    known = np.flatnonzero(seen >= 0)
    unused = np.ones(len(conf), dtype=bool)
    if len(known) and len(conf):
        age = step - seen[known]
        # Cap extrapolation so a long absence cannot send a prediction arbitrarily far.
        predicted = pos[known] + vel[known] * np.minimum(age, 3)[:, None]
        dist = np.linalg.norm(predicted[:, None] - centers, axis=2)
        cost = dist + YOLO_TRL_CONF_PX * (1 - conf)
        if YOLO_TRL_GATE_PX is not None:
            gate = YOLO_TRL_GATE_PX * np.sqrt(age)
            cost[dist > gate[:, None]] = np.inf
            # Each track may take a dummy column (a missed observation).
            miss = (1 + cost[np.isfinite(cost)].sum())
            cost = np.column_stack((cost, np.full((len(known), len(known)), miss)))
        rows, cols = yolo_trl_hungarian(cost)
        real = cols < len(conf)
        ids, cols = known[rows[real]], cols[real]
        points[ids] = centers[cols]
        vel[ids] = (points[ids] - pos[ids]) / (step - seen[ids])[:, None]
        unused[cols] = False

    # Seed never-seen IDs by confidence, then assign them left-to-right.
    fresh = np.flatnonzero(seen < 0)
    remaining = np.flatnonzero(unused)
    ranked = remaining[np.argsort(-conf[remaining], kind="stable")[:len(fresh)]]
    selected = ranked[np.lexsort((centers[ranked, 1], centers[ranked, 0]))]
    points[fresh[:len(selected)]] = centers[selected]
    visible = points[:, 0] >= 0
    pos[visible] = points[visible]
    seen[visible] = step
    return points


@server
def yolo_trl_frame(server):
    result = server.yolo_trl_model.predict(
        server.current_frame,
        device=YOLO_TRL_DEVICE,
        classes=YOLO_TRL_CLASSES,
        conf=YOLO_TRL_CONF,
        max_det=max(300, 2 * server.n_ind),
        verbose=False,
    )[0]

    boxes = result.boxes
    if boxes is None:
        raise ValueError("Use YOLO weights that return detection boxes.")

    # SciPy's Hungarian assignment uses CPU arrays.
    centers = boxes.xywh[:, :2].detach().cpu().numpy()
    scores = boxes.conf.detach().cpu().numpy()
    points = yolo_trl_assign(server, centers, scores)
    server.meas_last, server.meas_now = server.meas_now, points.tolist()

    if server.draw:
        for track_id, (x, y) in enumerate(points):
            if x >= 0:
                center = (round(x), round(y))
                yolo_trl_cv.circle(server.current_frame, center, 4, (0, 255, 0), 2)
                yolo_trl_cv.putText(
                    server.current_frame, str(track_id), center,
                    yolo_trl_cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                )

    data, clock = server.databuffer, server.clockbuffer
    server.semaphore.acquire()
    try:
        data[:, :, :-1] = data[:, :, 1:]
        clock[:-1] = clock[1:]
        clock[-1] = (
            yolo_trl_time.time() - server.t_init
            if server.vid_source_type == "cam"
            else server.frame_index / server.fps
        )
        data[:, :, -1] = points
        server.framesbuffer[:-1] = server.framesbuffer[1:]
        server.framesbuffer[-1] = server.current_frame.copy()

        if server.keep_video.value:
            if not server.recorded_frames:
                server.recorded_frames.extend(
                    fr for fr in server.framesbuffer if fr is not None
                )
            else:
                server.recorded_frames.append(server.current_frame)

        if server.keep_recordings.value:
            if not server.recorded_points:
                server.recorded_points.extend(list(data))
                server.recorded_times.extend(list(clock))
            else:
                server.recorded_points.append(data[:, :, -1])
                server.recorded_times.append(clock[-1])

        if server.write_video.value:
            server.vidout.write(server.current_frame)

        if server.write_recordings.value:
            print(clock[-1], *points.ravel(), sep=",", file=server.recout, flush=True)
    finally:
        server.semaphore.release()
# CASSETTE ENDS: YOLO_SERVER_TRACKING



# CASSETTE BEGINS: ROTATING_CROSSHAIRS
# DESCRIPTION: Draws rotating green crosshairs around all detected
# individuals and saves the annotated video.
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES:
RC_SIZE = 40               # Circle diameter in pixels
RC_COLOR = (0, 255, 0)      # Bright green (BGR)
RC_THICKNESS = 2            # Line thickness
RC_PROTRUSION = 15          # Extension beyond circle
RC_ROTATION_SPEED = 3.0     # Degrees per frame
RC_OUTPUT_FILE = "rotating_crosshairs.mp4"
# KNOWN ISSUES: None

@server.startfunc
def rotating_crosshairs_setup(server):
    server.rc_angle = 0.0
    server.keep_video.value = True

@server
def rotating_crosshairs(server):
    if server.framesbuffer[-1] is None:
        return
    frame = server.framesbuffer[-1].copy()

    data, clock = server.get_data_and_clock()
    positions = data[:, :, -1]

    radius = RC_SIZE // 2
    arm_length = radius + RC_PROTRUSION

    angle = np.deg2rad(server.rc_angle)
    ca, sa = np.cos(angle), np.sin(angle)

    for x, y in positions:
        if not np.isfinite([x, y]).all() or x < 0 or y < 0:
            continue

        cx, cy = int(round(x)), int(round(y))

        # Stationary circle
        cv2.circle(frame, (cx, cy), radius,
                   RC_COLOR, RC_THICKNESS, cv2.LINE_AA)

        # Rotating cross
        for dx, dy in ((ca, sa), (-sa, ca)):
            p1 = (int(round(cx - arm_length * dx)),
                  int(round(cy - arm_length * dy)))
            p2 = (int(round(cx + arm_length * dx)),
                  int(round(cy + arm_length * dy)))

            cv2.line(frame, p1, p2,
                     RC_COLOR, RC_THICKNESS, cv2.LINE_AA)

    server.rc_angle = (server.rc_angle + RC_ROTATION_SPEED) % 360.0
    server.framesbuffer[-1] = frame
    if server.keep_video.value and server.recorded_frames:
        server.recorded_frames[-1] = frame.copy()

@server.stopfunc
def rotating_crosshairs_save(server):
    server.dumpvideo(outfile=RC_OUTPUT_FILE)

# CASSETTE ENDS: ROTATING_CROSSHAIRS


trl.run_trsession(server, semm)
