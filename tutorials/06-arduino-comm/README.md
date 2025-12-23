# TracktorLive Tutorial 6: Message an Arduino

**Note for WSL users**: This tutorial assumes that you have followed the [additional steps](../../DOCS/COMPORT.md) 
necessary to access an Arduino.

## Goal

To automatically message an Arduino board when a condition is met.
An [Arduino](https://www.arduino.cc/) is a device that can provide an interface
between your computer and a circuit designed by you. This is one way you can
create dynamic responses to the actions of animals in your lab environment. In
this tutorial, we will demonstrate three examples.
In the first two examples, we will briefly turn on a red LED when an animal (an
ant and a mouse respectively)
enters a region of interest. We will explain the first example in detail.
In the third example, we will open a door when
a pair of animals (pillbugs) are both located in the same region of interest.


## Method

We will make use of the [Message
Arduino](../../Library_Of_Casettes/Message_Arduino/message_arduino.md) cassette
to run this tutorial. The python scripts automatically handle conveying single
characters (a letter, number, or symbol) 
to a connected Arduino board. We have also provided the `.ino` scripts to
be flashed onto the Arduino itself, by which the Arduino is programmed to respond
to incoming information from TracktorLive. (If you would like to learn more
about flashing code onto an Arduino, or in general, about how one uses an
Arduino, refer to the tutorials on the [offical Arduino
website](https://docs.arduino.cc/learn/).)

Consider the python `stimulus_ant.py`, where an LED is to be turned on each time
an ant enters a circlular region of interest in its arena.
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

When the python script is run, each time the ant enters the circle, the character 'm' is
transmitted to the Arduino, which uses this information to light up an LED (see
`led_trigger.ino`).

![](ant_led.gif)

As you can see in the above GIF, the LED in the bottom-left of the GIF always
shines briefly whenever the ant enters the green circle.

We replicate this example with a mouse with the code provided in
`stimulus_mouse.py`.

As a third, more interactive example, we would like the Arduino to open
a 'door' for a pair of pill-bugs when they are both located in the same
user-specified region of interest.
The file `door_pillbug.py` transmits the characters 'm' and 'k' to instruct an
Arduino to either open or close a door respectively (see video below). This example has many
additional customisations, and we encourage you to read both the python
script and the Arduino script `openDoorsCopy.ino` to understand how you can customise them to your
needs. 


https://github.com/user-attachments/assets/009591e2-2d35-4dc5-a173-55abe1ab010a


## Use-cases

As you can imagine, connecting an Arduino to a computer and programming it to
dynamically respond to animals' positions can be of great use. We have already
discussed several use-cases with potential users of TracktorLive, such as in
automatic animal entrance/exit management in specific arenas, food dispensing
systems in habituation experiments, and experiments to study cognitive abilities.
An Arduino can also prove useful in several situations to improve experimenters'
ease-of-life for repetitive experiments.
