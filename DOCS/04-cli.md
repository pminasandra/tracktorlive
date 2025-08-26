# CLI usage

The library TracktorLive ships with the command-line utility `tracktorlive`
which provides quick ways of running many of the utilities needed for a basic
tracking session. 
The command `tracktorlive` becomes available on your shell as soon as you
install our library. `tracktorlive -h` shows you a list of options. 

1. **Getting param values:** The first and most important
thing you can do with the program is get the parameters needed for tracking with
your camera or pre-recorded video. 
These values are used by the underlying Tracktor engine to perform object
tracking.
For instance, if you have a single camera
connected, in your terminal, you can use:

    ```bash
    tracktorlive gui --camera 0
    ```

    To get parameters from a pre-recorded video, use:

    ```bash
    tracktorlive gui --file /path/to/file
    ```

    The `tracktorlive gui` command also has an `--out /path/to/outfile.json`
    argument, by which you can directly store the output of the GUI parameter fixing
    method into a .json file. These files are important for launching servers.

    Press Esc to exit the GUI at any time.

2. **Launching simple servers:** The `tracktorlive` command can also launch
   naive servers without any casettes. This can be done as follows:

   ```bash
   tracktorlive track --camera 0 /path/to/params.json
   ```

    As before, `--file /path/to/file` can be used in place of `--camera 0`.
    Furthermore, the `tracktorlive track` subcommand can optionally take
    a `--feed-id <a-unique-identifier>` and `--numtrack <how-many-individuals>` arguments to
    customise tracking. The server's feed is displayed, and can be used in any
    client-program you wish to write.

    This command is incredibly helpful for quickly tracking objects in
    pre-recorded files. For instance, suppose a video, video.mp4, has in it five
    small animals. Using the command `tracktorlive gui --file video.mp4 --out params.json`, you
    will arrive at the parameter values needed for tracking.

    You can now simply run:

    ```bash
    tracktorlive track --file video.mp4 --num-track 5 --write-rec
    ```

    and the five animals will be tracked, and their outputs will be saved to a
    .csv file. Using the same params.json, you can also track other videos
    recorded in the same setup. This allows effectively code-free tracking of
    animals.

3. In case of unexplained bugs, the command `tracktorlive clear` attempts to
   refresh cached data.

[previous](03-installation.md) | [next](05-core-concepts.md)
