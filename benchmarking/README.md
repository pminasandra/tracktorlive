# Benchmarking TracktorLive

TracktorLive is primarily intended for low cost devices. We therefore
quantitatively benchmarked TracktorLive’s performance on a Raspberry Pi 4B Rev
1.4 (8GB RAM, Quad-core ARM Cortex-A72 processor, running at up to 1.5 GHz,
64-bit), a commonly used single-board computer. We simulated four circular
objects performing correlated random walks on a complex, colourful Perlin noise
background as a 30 FPS 1 hour video.

![simulated video](./a_out.gif)

The colour of the objects was chosen so that they would occasionally blend in
with the background. Roughly every fifty iterations, one of the simulated
objects chased and attached itself to another object for a full duration of 7.5
seconds. We created two variants of one cassette to detect these chase events:
one variant was a server cassette while the other was a client cassette. In the
server cassette version, all tasks were completed in one process sequentially.
This is analogous to other tools that do not leverage concurrency. In contrast,
the client cassette executed the same code in a separate parallel process. The
chase detection cassette effectively checks if a given dyad is within a certain
threshold distance of each other for
$\ge$ 2s, and logs such events to a csv file. See `tracker_server.py` and
`tracker_client.py` for details.

Additionally, a delay of 0.3 seconds was added to both cassettes as an
additional stand-in for various ‘blocking’ tasks, i.e., tasks that do not allow
the program to proceed until they are completed. The server itself also used the
[Color Select](../Library_Of_Casettes/Color_Select/color_select.md) cassette to
more effectively detect simulated objects, more accurately representing
a situation where added video processing is needed prior to tracking. The server
also wrote tracked locations to a CSV file on-the-fly. For benchmarking, we used
the [Benchmark
Server](../Library_Of_Casettes/Benchmark_Server/benchmark-server.md) cassette.

The simulated video input of the server was presented through the linux tool
`v4l2loopback`, which allowed a video input to be presented as if arriving through
a camera. Unlike providing a video file as input directly, with the `v4l2loopback`
system, programs could actually skip frames if they were not fast enough. The
same video input was repeated across both experimental scenarios, allowing
a rigorous comparison of real-time performance. See [Virtual Camera Setup
Instructions](virtual_camera_setup.md) for details on this framework.

We found that without concurrency, the Raspberry Pi processed input at around
2 FPS, whereas with concurrency, the throughput increased to 12 FPS (Table 3).
The RAM use was comparable in both situations, whereas the client-cassette used
increased processing power (as expected).  Without client-based concurrency, 92%
of frames were skipped every minute, whereas with concurrency, around 61% of
frames were skipped. Such performance on low-cost hardware like a Raspberry Pi
can facilitate closed-loop experiments with reduced investment.

| Metric | Server only | Server and client |
|---|---:|---:|
| Mean latency (ms) | 398.10 | 86.71 |
| P95 latency (ms) | 412.00 | 101.00 |
| Frame rate (FPS) | 2.47 | 12.30 |
| Skipped-frame rate (%) | 91.77 | 60.69 |
| Mean RAM (MB) | 380.12 | 384.94 |
| Peak RAM (MB) | 382.28 | 385.89 |
| Mean CPU (%) | 33.87 | 134.95 |
| Peak CPU (%) | 39.25 | 141.08 |
