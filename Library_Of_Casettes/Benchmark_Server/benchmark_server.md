---
title: benchmark_server
author: TracktorLive Cassette Maker GPT
description:  Low-overhead, interval-based server benchmarking.
known_issues: none
---

```python
# CASSETTE BEGINS: BENCHMARK_SERVER
# DESCRIPTION: Low-overhead, interval-based server benchmarking.
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES:

benchmark_INTERVAL_MIN = config.INTERVAL_MINS
benchmark_OUTFILE = "benchmark_server_cassette.parquet"
benchmark_RAM_SAMPLE_S = 1.0
benchmark_LATENCY_BIN_MS = 1.0
benchmark_LATENCY_MAX_MS = 2000.0

# INTERNALS

import os
import time
import math
import cv2
import psutil
import numpy as np
import pandas as pd


def _benchmark_reset(server):
    server._bm_count = 0
    server._bm_latency_sum = 0.0
    server._bm_hist = np.zeros(
        server._bm_nbins + 1, dtype=np.int64
    )
    server._bm_ram_sum = 0.0
    server._bm_ram_count = 0
    server._bm_ram_peak = 0.0
    server._bm_cpu_sum = 0.0
    server._bm_cpu_peak = 0.0
    server._bm_cpu_count = 0
    server._bm_skipped = 0
    server._bm_index_valid = True


def _benchmark_flush(server, end):
    start = server._bm_interval_start
    dt = end - start
    n = server._bm_count

    if dt <= 0:
        return

    # Approximate p95 using fixed-width latency histogram.
    if n:
        target = math.ceil(0.95 * n)
        p95_bin = int(np.searchsorted(
            np.cumsum(server._bm_hist), target
        ))
        p95 = p95_bin * benchmark_LATENCY_BIN_MS
    else:
        p95 = None

    if server.vid_source_type == "cam":
        expected = round(server._bm_fps * dt)
        skipped = max(0, expected - n)
        expected = max(expected, n)
    elif server._bm_index_valid:
        skipped = server._bm_skipped
        expected = n + skipped
    else:
        skipped = None
        expected = None

    server._bm_rows.append({
        "feed_id": server.feed_id,
        "input_type": server.vid_source_type,
        "interval": server._bm_interval,
        "interval_start_s": start - server._bm_start,
        "interval_end_s": end - server._bm_start,
        "duration_s": dt,
        "nominal_fps": server._bm_fps,
        "frames_processed": n,
        "frames_expected": expected,
        "skipped_frames": skipped,
        "skipped_frame_rate": (
            skipped / expected
            if expected is not None and expected > 0
            else None
        ),
        "actual_fps": n / dt,
        "latency_mean_ms": (
            server._bm_latency_sum / n if n else None
        ),
        "latency_p95_ms": p95,
        "ram_mean_mb": (
            server._bm_ram_sum / server._bm_ram_count
            if server._bm_ram_count else None
        ),
        "ram_peak_mb": (
            server._bm_ram_peak
            if server._bm_ram_count else None
        ),
        "cpu_mean_percent": (
            server._bm_cpu_sum / server._bm_cpu_count
            if server._bm_cpu_count else None
        ),
        "cpu_peak_percent": (
            server._bm_cpu_peak
            if server._bm_cpu_count else None
        ),
    })

    server._bm_interval += 1
    server._bm_interval_start = end
    _benchmark_reset(server)


@server.startfunc
def benchmark_setup(server):
    if benchmark_INTERVAL_MIN <= 0:
        raise ValueError("Interval must be positive")

    server._bm_start = time.perf_counter()
    server._bm_interval_start = server._bm_start
    server._bm_interval_s = benchmark_INTERVAL_MIN * 60
    server._bm_interval = 0
    server._bm_rows = []

    server._bm_proc = psutil.Process(os.getpid())
    server._bm_proc.cpu_percent(interval=None)
    server._bm_last_ram_sample = server._bm_start

    fps = server.cap.get(cv2.CAP_PROP_FPS)
    server._bm_fps = (
        float(fps)
        if math.isfinite(fps) and fps > 0
        else float(server.fps)
    )

    server._bm_nbins = max(
        1,
        int(benchmark_LATENCY_MAX_MS /
            benchmark_LATENCY_BIN_MS)
    )

    server._bm_last_index = None
    _benchmark_reset(server)

    original = server._eachframe

    def measured_frame(cap, databuffer, clockbuffer):
        t0 = time.perf_counter()

        result = original(cap, databuffer, clockbuffer)

        t1 = time.perf_counter()

        # EOF or stopped: no successfully processed frame.
        if not server.running.value:
            return result

        # Complete elapsed intervals.
        while (
            t1 - server._bm_interval_start
            >= server._bm_interval_s
        ):
            end = (
                server._bm_interval_start
                + server._bm_interval_s
            )
            _benchmark_flush(server, end)

        # Latency accumulation.
        latency_ms = (t1 - t0) * 1000.0
        server._bm_count += 1
        server._bm_latency_sum += latency_ms

        bucket = min(
            int(latency_ms / benchmark_LATENCY_BIN_MS),
            server._bm_nbins
        )
        server._bm_hist[bucket] += 1

        # Source frame gaps: video files only.
        if server.vid_source_type == "file":
            index = int(server.frame_index)

            if index < 0:
                server._bm_index_valid = False
            elif server._bm_last_index is not None:
                server._bm_skipped += max(
                    0, index - server._bm_last_index - 1
                )

            if index >= 0:
                server._bm_last_index = index

        # Sample memory and CPU periodically, not per frame.
        if (
            t1 - server._bm_last_ram_sample
            >= benchmark_RAM_SAMPLE_S
        ):
            ram = (
                server._bm_proc.memory_info().rss
                / 1048576
            )

            server._bm_ram_sum += ram
            server._bm_ram_count += 1
            server._bm_ram_peak = max(
                server._bm_ram_peak, ram
            )

            cpu = server._bm_proc.cpu_percent(interval=None)
            server._bm_cpu_sum += cpu
            server._bm_cpu_count += 1
            server._bm_cpu_peak = max(
                server._bm_cpu_peak, cpu
            )

            server._bm_last_ram_sample = t1

        return result

    server._eachframe = measured_frame


@server.stopfunc
def benchmark_save(server):
    end = time.perf_counter()

    # Flush any full intervals, including empty ones.
    while (
        end - server._bm_interval_start
        >= server._bm_interval_s
    ):
        boundary = (
            server._bm_interval_start
            + server._bm_interval_s
        )
        _benchmark_flush(server, boundary)

    # Flush the final partial interval.
    if end > server._bm_interval_start:
        _benchmark_flush(server, end)

    pd.DataFrame(server._bm_rows).to_parquet(
        benchmark_OUTFILE, index=False
    )

    print(f"Benchmark saved: {benchmark_OUTFILE}")

# CASSETTE ENDS: BENCHMARK_SERVER
```
