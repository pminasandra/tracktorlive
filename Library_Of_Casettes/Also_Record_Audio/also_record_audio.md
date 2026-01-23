---
title: also_record_audio
author: Pranav Minasandra
description: Record audio with ffmpeg in a separate process and muxes it into the recorded video at the end.
known_issues: ffmpeg needs to be installed.
---

**Notes**:

1. It is up to the user to make sure `ffmpeg` is installed and available on
   their machine to run this cassette.
2. A command is printed when the Tracktor Server exits. This command must be
   copied and run as is.

```python
# CASSETTE BEGINS: ALSO_RECORD_AUDIO
# DESCRIPTION: Record audio with ffmpeg in a separate process and muxes it into the recorded video at the end.
# AUTHOR: TracktorLive Cassette Maker GPT
#
# USER DEFINED VARIABLES:
audrec_PATH_TO_FFMPEG = "ffmpeg"  # or absolute path, e.g. "/usr/bin/ffmpeg"

# Audio capture backend (edit for your OS):
#   Linux (ALSA):       ["-f","alsa","-i","default"]
#   macOS (avfoundation): ["-f","avfoundation","-i",":0"]   # often needs permission + correct device index
#   Windows (dshow):    ["-f","dshow","-i","audio=Microphone (Your Device Name)"]
audrec_FFMPEG_AUDIO_INPUT_ARGS = ["-f", "alsa", "-i", "default"]

# WAV encoding options (keep PCM for maximum compatibility)
audrec_WAV_ARGS = ["-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le"]

# When muxing, audio codec to store inside the video container (typical for MP4)
audrec_MUX_AUDIO_CODEC_ARGS = ["-c:a", "aac", "-b:a", "192k"]

# If True: replace server.vidfilename with an audio-muxed version (via temp file + rename)
audrec_OVERWRITE_VIDEO_IN_PLACE = True

# INTERNALS (do not edit unless you know what you're doing)
audrec__stop_evt = None
audrec__proc = None
audrec__audio_started_t = None
audrec__wav_path = None

def audrec__audio_worker(stop_evt, started_conn, ffmpeg_path, ffmpeg_in_args, wav_args, wav_out_path):
    import subprocess, time, signal
    # Launch ffmpeg recorder; report "precise" start time right after spawning
    cmd = [ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error"] + ffmpeg_in_args + wav_args + [wav_out_path]
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        started_conn.send(time.time())
    except Exception:
        try:
            started_conn.send(None)
        except Exception:
            pass
        return
    finally:
        try:
            started_conn.close()
        except Exception:
            pass

    # Wait until asked to stop, then stop ffmpeg cleanly
    try:
        while not stop_evt.is_set():
            if p.poll() is not None:
                break
            time.sleep(0.01)
    finally:
        if p.poll() is None:
            try:
                p.send_signal(signal.SIGINT)
                p.wait(timeout=2.0)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        try:
            p.wait(timeout=0.5)
        except Exception:
            pass

@server.startfunc
def audrec__start(server):
    import multiprocessing as mp
    import os, time, ulid

    global audrec__stop_evt, audrec__proc, audrec__audio_started_t, audrec__wav_path

    os.makedirs(server.feed_id, exist_ok=True)
    audrec__wav_path = os.path.join(server.feed_id, f"{server.feed_id}_aud_{str(ulid.ULID())}.wav")

    audrec__stop_evt = mp.Event()
    parent_conn, child_conn = mp.Pipe(duplex=False)

    audrec__proc = mp.Process(
        target=audrec__audio_worker,
        args=(
            audrec__stop_evt,
            child_conn,
            audrec_PATH_TO_FFMPEG,
            audrec_FFMPEG_AUDIO_INPUT_ARGS,
            audrec_WAV_ARGS,
            audrec__wav_path,
        ),
    )
    audrec__proc.start()

    # Receive worker-reported start time (fallback to now if not available)
    try:
        if parent_conn.poll(2.0):
            audrec__audio_started_t = parent_conn.recv()
        else:
            audrec__audio_started_t = None
    except Exception:
        audrec__audio_started_t = None
    finally:
        try:
            parent_conn.close()
        except Exception:
            pass

    if audrec__audio_started_t is None:
        audrec__audio_started_t = time.time()

@server.stopfunc
def audrec__stop(server):
    import os, time, subprocess, shutil

    global audrec__stop_evt, audrec__proc, audrec__audio_started_t, audrec__wav_path

    # Stop audio process
    try:
        if audrec__stop_evt is not None:
            audrec__stop_evt.set()
    except Exception:
        pass

    try:
        if audrec__proc is not None and audrec__proc.is_alive():
            audrec__proc.join(timeout=3.0)
    except Exception:
        pass

    try:
        if audrec__proc is not None and audrec__proc.is_alive():
            audrec__proc.terminate()
            audrec__proc.join(timeout=1.0)
    except Exception:
        pass

    # If not writing video, just keep the wav and exit
    if not bool(server.write_video.value):
        return

    # Determine video path
    vid_path = getattr(server, "vidfilename", None)
    if vid_path is None:
        # fallback: some versions may not store vidfilename; user requested server.vidfilename though
        return

    if audrec__wav_path is None or (not os.path.exists(audrec__wav_path)):
        return

    # Compute sync correction using server.t_run_begin (set after @server.startfunc hooks) vs audio start
    #   delta > 0  => audio started AFTER video started   => delay audio by delta (itsoffset)
    #   delta < 0  => audio started BEFORE video started  => trim audio by -delta (ss)
    try:
        delta = float(audrec__audio_started_t) - float(server.t_run_begin)
    except Exception:
        delta = 0.0

    ff = audrec_PATH_TO_FFMPEG
    tmp_out = vid_path + ".audmux_tmp" + os.path.splitext(vid_path)[1]

    # Build ffmpeg mux command
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", vid_path]

    if delta > 0:
        cmd += ["-itsoffset", f"{delta:.6f}", "-i", audrec__wav_path]
    elif delta < 0:
        cmd += ["-ss", f"{(-delta):.6f}", "-i", audrec__wav_path]
    else:
        cmd += ["-i", audrec__wav_path]

    # Map video from input0, audio from input1; keep video stream copy, re-encode audio
    cmd += [
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        *audrec_MUX_AUDIO_CODEC_ARGS,
        "-shortest",
        tmp_out,
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # If mux fails, do not delete the WAV (user can inspect)
        return

    # Replace original video (optional)
    if audrec_OVERWRITE_VIDEO_IN_PLACE:
        try:
            os.replace(tmp_out, vid_path)
        except Exception:
            # If replace fails, keep tmp output
            pass
    else:
        # If not overwriting, leave tmp_out as additional file
        pass

    # Delete WAV after successful mux
    try:
        os.remove(audrec__wav_path)
    except Exception:
        pass
# CASSETTE ENDS: ALSO_RECORD_AUDIO
```
