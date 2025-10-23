# TracktorLive Tutorial 6: Message an Arduino

**Note for WSL users**: This tutorial assumes that you have followed the [additional steps](../../DOCS/COMPORT.md) 
necessary to access an Arduino.

## Goal

An [Arduino](https://www.arduino.cc/) is a device that can provide an interface
between your computer and a circuit designed by you. This is one way you can
create dynamic responses to the actions of animals in your lab environment. In
this tutorial, we will demonstrate three examples (of which we will explain one
in detail). In the first two examples, we will turn on a red LED when an animal
gets inside a region of interest. In the last example, we will open a door when
a pair of animals are within the same region of interest.


## Method

We will make use of the [Message Arduino](../../Library_Of_Casettes/Message_Arduino/message_arduino.md) cassette
to run this tutorial. 
The python script automatically handles conveying single characters to
a connected Arduino board. We have also provided `.ino` scripts to be flashed
onto the Arduino itself, by which we tell that device how to respond to incoming
information from TracktorLive.

Consider the file `stimulus_ant.py`, where an LED is to be turned on each time
an ant steps into a circle.
In general, the Message Arduino cassette requires a user-selected
`condition_func` function, which returns either a single character or `None`.
If it receives a character, it will automatically transmit it to the connected
Arduino.

For detecting when an ant enters a specific region, we can use the following
`condition_func`:

```python
# First, define a 'condition_func' function that returns either a character or None.
def _in_circle(locs, center=dwchl_center, radius=dwchl_radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

# Then, return 'm' if the ant is in the circle.
def condition_func(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]
    if _in_circle(curr_loc) and not _in_circle(prev_loc):#ant just moved into the circle
       return 'm'
    return None
```

When the file is run, each time the ant enters the circle, the character 'm' is
transmitted to the Arduino, which uses this information to light up an LED (see
`led_trigger.ino`).

![](ant_led.gif)

As you can see in the above GIF, the LED in the bottom right of the GIF always
shines briefly whenever the ant enters the green rectangle.
