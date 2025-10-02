# tracktorlive/__main__.py
# Pranav Minasandra

import argparse
import json
import os
import os.path
import re
import sys

import tracktorlive as trl

def parse_resolution(res_string):
    """
    Parses a resolution string of the form 'WIDTHxHEIGHT' or 'WIDTH×HEIGHT'.
    
    Parameters:
    - res_string (str): The input resolution string, e.g., '1920x1080' or '1920×1080'.
    
    Returns:
    - tuple: (width, height) as integers.
    
    Raises:
    - ValueError: If the input format is invalid.
    """
    match = re.fullmatch(r"\s*(\d+)\s*[x×]\s*(\d+)\s*", res_string)
    if not match:
        raise ValueError(f"Invalid resolution format: '{res_string}'")
    
    width, height = map(int, match.groups())
    return width, height


def run_gui(args):
    cap = None
    vidtype = None

    if args.camera is not None:
        cap = int(args.camera)
        vidtype = "cam"
    elif args.file is not None:
        cap = args.file
        vidtype = "file"
    else:
        print("Error: Please specify either --camera or --file", file=sys.stderr)
        sys.exit(1)

    if args.res is not None:
        width, height = parse_resolution(args.res)
    else:
        width, height = 640, 480

    configdict = None
    if args.out is not None:
        if os.path.exists(args.out):
            configdict=trl.paramfixing.load_config(args.out)

    cap = trl.trackutils.get_vid(cap)
    params = trl.get_params_from_gui(cap, vidtype, initial_config=configdict, write_file=args.out, width=width, height=height)
    cap.release()

    if args.out is None:
        print(json.dumps(params, indent=4))


def run_track(args):
    with open(args.paramsfile) as f:
        params = json.load(f)

    if args.camera is not None:
        source = int(args.camera)
        realtime = True
    elif args.file is not None:
        source = args.file
        realtime = False
    else:
        print("Error: Please specify either --camera or --file", file=sys.stderr)
        sys.exit(1)

    if args.res is not None:
        width, height = parse_resolution(args.res)
    else:
        width, height = 640, 480

    write_recordings = args.write_rec
    write_video = args.write_vid

    if "fps" not in params:
        print("Error: 'fps' must be included in the parameter file", file=sys.stderr)
        sys.exit(1)

    if args.numtrack is not None:
        n_ind = int(args.numtrack)
    else:
        n_ind = 1

    if args.timeout is not None:
        timeout = args.timeout
    else:
        timeout = None

    server, semm = trl.spawn_trserver(
        source,
        params=params,
        n_ind=n_ind,
        feed_id=args.feed_id,
        realtime=realtime,
        timeout=timeout,
        write_video=write_video,
        write_recordings=write_recordings,
        width=width,
        height=height
    )

    if args.show_display:#Should real time tracking be shown?
        import cv2
        wname = f"Tracking for {server.feed_id}"
        @server.startfunc
        def showsetup(server):
            server.draw = True
            server.show_flag = True
            cv2.namedWindow(wname, cv2.WINDOW_NORMAL)

        @server
        def show(server):
            if server.show_flag:
                frame = server.framesbuffer[-1]
                if frame is None:
                    return
                cv2.imshow(wname, server.framesbuffer[-1])
                key = cv2.waitKey(1)

                if key==27 or key==ord('q'):
                    server.show_flag = False
                    cv2.destroyWindow(wname)
        
        @server.stopfunc
        def showcleanup(server):
            if server.show_flag:
                cv2.destroyWindow(wname)

    print(f"Tracking initiated at feed_id: {server.feed_id}")
    trl.run_trsession(server, semm)


def run_clear(_):
    feeds_dir = trl.FEEDS_DIR
    clients_dir = trl.CLIENTS_DIR

    print("Warning: This will remove all feed/client files.")
    print("Active servers and clients may be affected.")
    confirm = input("Proceed? [y/N]: ").lower()
    if confirm != "y":
        print("Aborted.")
        return

    for directory in [feeds_dir, clients_dir]:
        if os.path.exists(directory):
            for fname in os.listdir(directory):
                path = os.path.join(directory, fname)
                try:
                    os.remove(path)
                    print(f"Deleted: {path}")
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")


tr_help = f"""tracktorlive 0.9.0-beta
TracktorLive: Real-time tracking and response delivery for behavioural
experiments.

TracktorLive was created by {trl.__author__}, and is provided as-is under a
{trl.__license__} license.  (see LICENSE for further details.) TracktorLive is
powered by Tracktor, and is designed to run on low computational power, frugal
systems. To know more:

TracktorLive: {trl.__url__}
Tracktor: https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.13166
DOCS: {trl.__url__}/DOCS.md
"""

def main():
    parser = argparse.ArgumentParser(
                                prog="tracktorlive",
                                description=tr_help,
                                formatter_class=argparse.RawDescriptionHelpFormatter
                            )
    subparsers = parser.add_subparsers(dest="command")

    # GUI subcommand
    gui_parser = subparsers.add_parser("gui", help="Open parameter tuning GUI")
    gui_parser.add_argument("--camera", "-c", help="Camera index", type=int)
    gui_parser.add_argument("--file", "-f", help="Video file path")
    gui_parser.add_argument("--out", "-o", help="Output JSON file path")
    gui_parser.add_argument("--res", "-r", help="Video resolution, e.g., 640x480", default="640x480")

    # Track subcommand
    track_parser = subparsers.add_parser("track", help="Start a tracking server")
    track_parser.add_argument("paramsfile", help="JSON parameter file")
    track_parser.add_argument("--camera", "-c", help="Camera index", type=int)
    track_parser.add_argument("--file", "-f", help="Video file path")
    track_parser.add_argument("--feed-id", "-I", help="Feed ID", default=None)
    track_parser.add_argument("--numtrack", "-n", help="Number of recorded individuals.", default=1, type=int)
    track_parser.add_argument("--write-rec", "-w", help="Whether tracking should be output to a csv file", action='store_true')
    track_parser.add_argument("--write-vid", "-d", help="Whether video should be recorded to a file", action='store_true')
    track_parser.add_argument("--show-display", "-s", help="Whether tracking should be displayed", action='store_true')
    track_parser.add_argument("--timeout", "-t", help="How many seconds before server should shut down", type=int)
    track_parser.add_argument("--res", "-r", help="Video resolution, e.g., 640x480", default="640x480")

    # Clear subcommand
    clear_parser = subparsers.add_parser("clear", help="Remove all feed/client files")

    args = parser.parse_args()

    if args.command == "gui":
        run_gui(args)
    elif args.command == "track":
        run_track(args)
    elif args.command == "clear":
        run_clear(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

