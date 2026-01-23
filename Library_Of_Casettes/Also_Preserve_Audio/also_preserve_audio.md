---
title: also_record_audio
author: Pranav Minasandra (TracktorLive Cassette Maker GPT)
description: Extract audio from input video and muxes it into the output video at the end.
known_issues: None
---

**Notes**:

1. It is up to the user to make sure `ffmpeg` is installed and available on
   their machine to run this cassette.
2. This is only applicable for `realtime=False`, so for working of pre-recorded
   videos.

```python
# CASSETTE BEGINS: ALSO_PRESERVE_AUDIO
# DESCRIPTION: If server is processing a *file* (not a cam feed) AND server.write_video is True,
#              then at shutdown, mux the original audio from the input video into server.vidfilename.
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES:
ALSO_PRESERVE_AUDIO_FFMPEG_PATH = "ffmpeg"  # set to full path if ffmpeg is not on PATH
# KNOWN ISSUES: If input has no audio, output remains video-only.

def _apa__flag_true(x):
    return bool(getattr(x, "value", x))

@server.stopfunc
def also_preserve_audio__mux_at_end(server):
    # Only relevant when writing video
    if not _apa__flag_true(getattr(server, "write_video", False)):
        return

    # Only work for file inputs (not camera IDs)
    vidinput = getattr(server, "vidinput", None)
    if not isinstance(vidinput, str):
        return

    outpath = getattr(server, "vidfilename", None)
    if not isinstance(outpath, str) or not outpath:
        return

    import os
    import subprocess

    base, ext = os.path.splitext(outpath)
    tmp_out = f"{base}__with_audio__tmp{ext}"

    cmd = [
        ALSO_PRESERVE_AUDIO_FFMPEG_PATH, "-y",
        "-i", outpath,      # processed video (video stream)
        "-i", vidinput,     # original input (audio stream)
        "-map", "0:v:0",
        "-map", "1:a?",
        "-c:v", "copy",
        "-c:a", "copy",
        "-shortest",
        tmp_out,
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(tmp_out, outpath)
    except Exception:
        # Best-effort cleanup
        try:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)
        except Exception:
            pass

# CASSETTE ENDS: ALSO_PRESERVE_AUDIO
```
