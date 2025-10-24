# TracktorLive Tutorial 8: Video registration

-------------------------

# Disclaimer:

As an experiment, we have used the GenAI, ChatGPT 5, to write one cassette for
us. This is not to be taken as advice or endorsement of this or other Large
Language Models in scientific coding.

-------------------------

## Goal

We will go back to the video of 8 termites we encountered in Tutorial 2.

![](termite_video.gif)

To truly focus on the behaviour of each individual, we would like to program
a birds-eye pseudo-camera to follow each individual around as it moves, and
store this birds-eye cropped video feed.

## Method

We will use the same `termite_video.mp4` and `termite-video-params.json` as
before. As an experiment, I provided a description of TracktorLive and the task
to ChatGPT 5. With a few rounds of back-and-forth, it arrived at the 
[First Person Views](../../Library_Of_Casettes/First_Person_Views/first_person_views.md)
cassette. The cassette has not been optimised by me, and is somewhat slow. As
you can see below, the individual cropped video feeds also rotate a bit more
than needed. However, overall, a first-person view is somewhat cleanly obtained.

![](termite_collage.gif)

(**TODO**: Provide a prompt for users to give to their own LLMs for their own
use-cases)

## Explanation

TracktorLive's modular cassette architecture may enable it to harmonise with
Generative AI technology such as ChatGPT, since the output required to get your
task done is minimal. This fairly complex example serves to prove this point.

We tried this exact cassette once again with our fish video from Tutorial 5. The
initial and final videos are shown below:

![](fish_video.gif)

![](fish_collage.gif)


