# TracktorLive Tutorials

Here are the tutorials that are currently available.
Each link sends you to a directory with all relevant files, and a README.md
containing the text of the tutorial. We recommend that you go through all these
tutorials in order to familiarise yourself with this software, and explore all
scripts and cassettes used in detail. Only a minimal working knowledge of python
is assumed in most cases.

**Note:** When a python script is indicated in the tutorial, you should run it as

```bash
python <filename>
```

or in some cases,

```bash
python3 <filename>
```

## Important notes

- Commands should be run as they are given, unless explicitly specified.
- Any text in command descrpitions between angular brackets, `<like this>`, is meant to be replaced.
- Any text in command descrpitions between square brackets, `[like this]`, is
  optional.
- We recommend going through all tutorials.

## List of tutorials

These tutorials start with basic tasks, and slowly build up in complexity
in Tutorials 1-6 where the user finally gets to interacting with
arduino boards and delivering tracking-based stimuli. While stimulus delivery is
one of the key requirements for which TracktorLive was built, it also goes
through other powerful functionalities where it controls the video feed. These
are covered in Tutorials 7 and 8.

1. [Recording a video](./01-recording-video/): Use TracktorLive to record
   a simple 10 minute video from the command line.
2. [Tracking objects](./02-tracking-object/): Track the positions of eight termites
   in a simple video, save these positions as CSV files.
3. [Tuning computer vision parameters](./03-tuning-params/): How to adopt
   TracktorLive to detect the animals in your specific setup.
4. [Applying cassettes to improve tracking](./04-tracking-in-complex-conditions/): How
   to use TracktorLive cassettes to optimise the tracking process.
5. [Automated response Delivery](./05-looming-video/): Write a script to play a looming
   stimulus video each time a fish moves above a certain velocity.
6. [Trigger an Arduino](./06-arduino-comm/): Communicate with a connected
   Arduino board and use it to automatically turn on lights or open doors in response to
   animal positions.
7. [Video chunking](./07-video-chunking/): Write a script to only record and
   save video when two animals are interacting with each other.
8. [Video centering'](./08-video-registration/): With a python script,
   extract cropped videos providing a top-down chasing view following each
   individual.

We also have [further demonstrations](./further-tutorials/), and are glad to see
submissions from our users to be included here.
