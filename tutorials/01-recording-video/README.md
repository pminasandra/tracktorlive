# TracktorLive Tutorial 1: Recording a video

This tutorial assumes that you have [installed](../../DOCS/03-installation.md)
TracktorLive correctly, and have your web-cam connected and
[accessible](../../DOCS/COMPORT.md).

## Goal

We will record one video that lasts 10 minutes from your web-cam. For this
tutorial, we don't care about actually tracking anything. Our goal is only to
record a video.

We will also assume that your camera is accessed using the `--camera 0`
argument. However, if you have more than one camera connected to your computer
(including the built-in webcam), you might need to use `1` or `2` (or `3` or...)
instead of `0`.


## Method

We will use the command-line utility, `tracktorlive`, that comes pre-installed
with this installation. Specifically, we will use the subcommand, `tracktorlive
track`. You can already try (and fail) by running this command:

```bash
tracktorlive track --camera 0
```

This is because the `tracktorlive track` subcommand expects to find *some*
information, in a json file, on how it should track objects in the video, even if we don't want
it to. We will get around this for now by creating a dummy json file with no
useful information for tracking. For this, we will use the powerful
`tracktorlive gui` subcommand:

1. Run the command: `tracktorlive gui --camera 0 --out params.json`.
2. When the GUI loads, tweak some of the parameters slightly.
3. Press <Esc> to exit the GUI and save a `params.json` file, which contains our
   dummy tracking information.

Finally, we are prepared to record the video.

Run the command

```bash
tracktorlive track --camera 0 --write-vid params.json --timeout 600
```

The `--timeout 600` ensures that the server exits after the specified number of
seconds. However, if you want to record a video of an arbitrary length, you can
launch the command without the `--timeout 600` argument, and simply press
`Ctrl+C` whenever you want to stop recording.

The video you desire should be saved as an mp4 file with a randomly generated
name.
