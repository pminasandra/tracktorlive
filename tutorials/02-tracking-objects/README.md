# TracktorLive Tutorial 2: Tracking objects

In this video, we will show you how to track 8 termites in a video without
writing any code. This folder contains a file named `masked_termite_video.mp4`,
in which you can see 8 termites in a Petri plate. We have also provided a file,
`termite-params.json`, which contains perfectly tuned parameters for object
tracking in this specific video. For this tutorial, we will directly use these
parameter values, but in the next tutorial, you will learn how to actually
arrive at those values with your own videos. You may also notice that the
background outside the Petri plate has been masked (appears black). This was
also done using TracktorLive, using the [Add Circular Mask](../../Library_Of_Casettes/Add_Circular_Mask/add_circular_mask.md) cassette.

![Tracks of the termites](tracks.png)

## Goal

We wish to track all 8 termites in this setup using one command, and get a .csv
file containing the tracking outputs. 

## Method

We will once again use the command-line utility, `tracktorlive`, to do this. The
utility works well for direct cases like this without much background
disturbance or lighting issues. More complex cases will need us to write code
and incorporate appropriate cassettes from the Library of Casettes.

The command we will run is:

```bash
tracktorlive track --file masked_termite_video.mp4 --numtrack 8 --write-rec termite-params.json
```

The required .csv file must appear in a newly generated folder. I have
visualised its output here near the start of the page.

### Explanation

The following table will explain what is going on above.

| Argument | Value | Description |
|----------|-------|-------------|
| `track` | — | Subcommand to start a tracking server. |
| `--file` | `masked_termite_video.mp4` | Path to the input video file. |
| `--numtrack` | `8` | Number of individuals to track simultaneously. |
| `--write-rec` | — | Save tracking results to a CSV file. |
| - | `termite-params.json` | JSON parameter file containing tracking settings (positional argument). |

The final argument is always your tracking information in a nice json file. Open
the file to see the format in which those instructions are stored.

If you also add the arguments `--show-display`, `tracktorlive` will show you the
highlighted positions of all termites as it is tracking them. 

### Use-case

If you have numerous videos recorded from the same experimental setup, this
command line tool can prove incredibly helpful to track them all. You just need
a shell for-loop to apply this command to every single video file.
