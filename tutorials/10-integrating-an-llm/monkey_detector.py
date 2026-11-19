import json
import time
import os

import cv2
import ollama
import tracktorlive as trl

with open("params.json") as jsonf:
    params = json.load(jsonf)



server, semm = trl.spawn_trserver("cam-trap-lowres.mp4",
                                    params,
                                    feed_id="monkey_detector",
                                    buffer_size=1,
                                    internal_tracking=False,
                                    realtime=False
                                 )

# CASSETTE BEGINS: LLM_USE_DETECT
# DESCRIPTION: Uses a Large Language Model to analyse incoming frame, chunk videos.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES: None
LLM_USE_COOLDOWN_TIME = 1.5#seconds
LLM_USE_EVERY_F_FRAMES = 10#frames
LLM_USE_MODEL = "gemma3:4b"
LLM_USE_PROMPT = (
    "Is there a monkey in the picture? "
    "Base your decision ONLY on the photograph. "
    "Respond with exactly YES or NO."
)# NOTE: Lines are automatically joined!
# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.

# CASSETTE INTERNALS:
def monkey_present(buffer):
    response = ollama.generate(
        model=LLM_USE_MODEL,
        prompt=LLM_USE_PROMPT,
        images=[buffer.tobytes()],
        options={
            "temperature": 0,
            "num_predict": 2,
        },
        think=False
    )
    res = response["response"].strip().upper()
    return res.startswith("YES")

@server.startfunc
def setup_server_time_controls(server):
    server.monkey_detected_bout_ongoing = False
    server.frcount = 0
    server.time_last = None
    server.monkey_detected_num = 0

@server
def llm_use_detect(server):
    server.frcount += 1
    if server.frcount >= LLM_USE_EVERY_F_FRAMES:
        server.frcount = 0
    if server.frcount > 0:
        return

    if server.time_last is not None:
        if time.time() - server.time_last < LLM_USE_COOLDOWN_TIME:
            return
    server.time_last = time.time()

    h, w = server.current_frame.shape[:2]
    scale = min(1.0, 512 / max(h, w))
    if scale < 1:
        frame = cv2.resize(
            server.current_frame,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA,
        )
    else:
        frame = server.current_frame.copy()
    _, buf = cv2.imencode(".jpg", frame)
    server._active_monkey_detection = monkey_present(buf)
    if server._active_monkey_detection:
        if not server.monkey_detected_bout_ongoing:
            server.monkey_detected_bout_ongoing = True
            print("Monkey detected.")
            server.monkey_detected_num += 1
            server.keep_video.value = True
            return

    
    if not server._active_monkey_detection:
        if server.monkey_detected_bout_ongoing:
            server.monkey_detected_bout_ongoing = False
            server.dumpvideo(f"monkey_{server.monkey_detected_num}.mp4")
            server.keep_video.value = False
            return

# CASSETTE ENDS: LLM_USE_DETECT
            
# CASSETTE BEGINS: DISPLAY_FEED
# DESCRIPTION: Displays current tracking from the server in real-time.
#   Press 'q' or <Esc> to close running display at any time.
# AUTHOR: Pranav Minasandra
# USER DEFINED VARIABLES: None
# KNOWN ISSUES: Does not work on Mac due to fork/spawn issues.
@server.startfunc
def show_live_feed_setup(server):
    server.show_flag = True
    cv2.namedWindow(server.feed_id, cv2.WINDOW_NORMAL)

@server
def show_live_feed_show(server):
    if server.show_flag:
        frame = server.current_frame
        if frame is None:
            return
        cv2.imshow(server.feed_id, frame)
        key = cv2.waitKey(1)

        if key==27 or key==ord('q'):
            server.show_flag = False
            cv2.destroyWindow(server.feed_id)

@server.stopfunc
def show_live_feed_cleanup(server):
    if server.show_flag:
        cv2.destroyWindow(server.feed_id)
# CASSETTE ENDS: SHOW_LIVE_FEED

trl.run_trsession(server, semm)
