# TracktorLive Tutorial 5.2: Turn on LED with Arduino based on individual position

This tutorial assumes that you have [installed](../../DOCS/03-installation.md)
TracktorLive correctly, and have your web-cam connected and
[accessible](../../DOCS/COMPORT.md).

## Goal

We will turn on a red LED when an ant gets inside a region of interest (ROI). 
In this case, our ROI is defined as the ant being close to a humidified cotton. 

## How It Works

1.  A video is analyzed frame by frame using real-time tracking.
2.  A user-defined function periodically checks whether the individual is inside or outside the ROI.
3.  When the individual is inside, we turn on the LED via an Arduino board for one second.

## Output

The video below shows how to run this example step-by-step.

https://github.com/user-attachments/assets/2a272be6-6ba1-4a76-b1d4-0ada6a84b93f

