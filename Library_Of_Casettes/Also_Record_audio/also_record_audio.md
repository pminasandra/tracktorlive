---
title: also_record_audio
author: Pranav Minasandra
description: Record audio with ffmpeg in a separate process and print a command to mux it into the recorded video at the end.
known_issues: ffmpeg needs to be installed. a command is printed, needs to be run * by the user *
---

**Notes**:

1. It is up to the user to make sure `ffmpeg` is installed and available on
   their machine to run this cassette.
2. A command is printed when the Tracktor Server exits. This command must be
   copied and run as is.

```python
# CASSETTE BEGINS: ALSO_RECORD_AUDIO
# AUTHOR: Pranav Minasandra
# DESCRIPTION: Record audio with ffmpeg in a separate process and mux it into the recorded video at the end.
#
# USER SPECIFIABLE DETAILS
AUDIO_DEVICE = None          # e.g. "default", "hw:0", "plughw:1,0", or Pulse device name; None -> "default"
AUDIO_INPUT_FMT = "alsa"     # "alsa" (most common), or "pulse"
AUDIO_SAMPLERATE = 48000     # Hz
AUDIO_CHANNELS = 1           # 1=mono, 2=stereo
AUDIO_OUTFILE = None         # None -> f"{server.feed_id}-audio.wav"
SYNC_OUTFILE = None          # None -> f"{server.feed_id}-audio-sync.json"
VIDEO_INFILE = None          # Path to the recorded video to mux into (must exist by ending)
MUXED_OUTFILE = None         # None -> f"{server.feed_id}-with-audio.mp4"
MUXED_SUFFIX = "-with-audio.mp4"
PATH_TO_FFMPEG = "ffmpeg"    # Default assumes 'ffmpeg' in PATH. Otherwise specify
                             # complete path to binary.
# KNOWN ISSUES: Requires ffmpeg installed; VIDEO_INFILE must be set to the final recorded video path.

#INTERNALS (DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING)

@server.startfunc
def also_record_audio_start(server):
    import time, subprocess, shutil, os.path

    if shutil.which("ffmpeg") is None:
        if not os.path.exists(PATH_TO_FFMPEG):
            raise RuntimeError("ALSO_RECORD_AUDIO couldn't find ffmpeg.")

    server._audio_device = "default" if AUDIO_DEVICE is None else str(AUDIO_DEVICE)
    server._audio_wav = AUDIO_OUTFILE or f"{server.feed_id}-audio.wav"

    cmd = [
        PATH_TO_FFMPEG, "-hide_banner", "-loglevel", "error",
        "-f", str(AUDIO_INPUT_FMT),
        "-ar", str(int(AUDIO_SAMPLERATE)),
        "-ac", str(int(AUDIO_CHANNELS)),
        "-i", server._audio_device,
        "-c:a", "pcm_s16le",
        "-y", server._audio_wav,
    ]

    server._audio_cmd = cmd
    server._audio_proc = subprocess.Popen(cmd)
    server.audio_t_init = time.time()

    # Register atexit fallback (will only actually run if mux cmd is later set)

# KNOWN ISSUES: The printed command must be run only after the mp4 has finalized (moov atom written).

@server.stopfunc
def print_mux_audio_cmd(server):
    import os, os.path, math, shutil

    ffmpeg = PATH_TO_FFMPEG if os.path.exists(PATH_TO_FFMPEG) else (shutil.which("ffmpeg") or PATH_TO_FFMPEG)

    audio_in = getattr(server, "_audio_wav", None)
    if not audio_in:
        print("[ALSO_RECORD_AUDIO] No server._audio_wav found; nothing to mux.")
        return

    feed_dir = str(getattr(server, "feed_id", ""))
    if not feed_dir or (not os.path.isdir(feed_dir)):
        print("[ALSO_RECORD_AUDIO] feed_id directory not found; cannot locate video.")
        return

    vids = sorted([v for v in os.listdir(feed_dir) if v.lower().endswith(".mp4")])
    if not vids:
        print("[ALSO_RECORD_AUDIO] No .mp4 files found in feed directory; nothing to mux.")
        return

    video_in = os.path.join(feed_dir, vids[-1])
    muxed_out = video_in[:-4] + MUXED_SUFFIX

    server_t0 = float(getattr(server, "t_init", float("nan")))
    audio_t0 = float(getattr(server, "audio_t_init", float("nan")))
    offset = audio_t0 - server_t0

    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]

    if (not math.isnan(offset)) and offset < 0:
        # audio earlier -> trim audio
        cmd += ["-ss", f"{abs(offset):.6f}", "-i", audio_in, "-i", video_in]
        audio_idx, video_idx = 0, 1
    else:
        # audio later/unknown -> delay audio
        delay = 0.0 if math.isnan(offset) else max(0.0, float(offset))
        cmd += ["-i", video_in, "-itsoffset", f"{delay:.6f}", "-i", audio_in]
        video_idx, audio_idx = 0, 1

    cmd += [
        "-map", f"{video_idx}:v:0",
        "-map", f"{audio_idx}:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        muxed_out,
    ]

    print("\n[ALSO_RECORD_AUDIO] Run this AFTER the mp4 has finished writing:")
    print(" ".join(cmd))

# CASSETTE ENDS: ALSO_RECORD_AUDIO
```
