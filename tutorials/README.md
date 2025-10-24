# TracktorLive Tutorials

Here are the tutorials that are currently available.
Each link sends you to a directory with all relevant files, and a README.md
containing the text of the tutorial. We recommend that you go through all these
tutorials in order to familiarise yourself with this software, and explore all
scripts and cassettes used in detail. Only a minimal working knowledge of python
is assumed in most cases.

**Note:** When a python file is indicated in the tutorial, you should run it as

```bash
python <filename>
```

or in some cases,

```bash
python3 <filename>
```

1. [Recording a video](./01-recording-video/): Use TracktorLive to record
   a simple 10 minute video from the command line.
2. [Tracking objects](./02-tracking-object/): Track the positions of eight termites
   in a simple video, save these positions as CSV files.
3. [Tuning computer vision parameters](./03-tuning-params/): How to adopt
   TracktorLive to detect the animals in your specific setup.
4. [Tracking in complex conditions](./04-tracking-in-complex-conditions/): How
   to use TracktorLive cassettes to optimise the tracking process.
5. [Response Delivery](./05-looming-video/): Write a script to play a looming
   stimulus video each time a fish moves above a certain velocity.
6. [Trigger an Arduino](./06-arduino-comm/): Communicate with a connected
   Arduino board and use it to automatically turn on lights or open doors in response to
   animal positions.
7. [Video chunking](./07-video-chunking/): Write a script to only record and
   save video when two animals are interacting with each other.
8. [Video lregistration'](./08-video-registration/): With a python script,
   extract cropped videos providing a first-person birds-eye view following each
   individual.

We also have [further demonstrations](./further-tutorials/), and are glad to see
submissions from our users to be included here.
