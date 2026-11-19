import subprocess
import shlex

def start_ffmpeg(cmd):
    """Start FFmpeg and return its process handle."""
    return subprocess.Popen( shlex.split(cmd), stdin=subprocess.PIPE)


def stop_ffmpeg(p):
    """Gracefully stop FFmpeg."""
    if p.poll() is not None:
        return

    try:
        p.stdin.write(b"q")
        p.stdin.flush()
        p.wait(timeout=5)
    except (BrokenPipeError,
            subprocess.TimeoutExpired):
        p.terminate()
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
    finally:
        p.stdin.close()
