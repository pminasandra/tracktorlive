---
title: message_arduino
author: Isaac Planas-Sitjà and Pranav Minasandra
description: When a user-defined function returns a character, transmits that character to a connected Arduino.
known_issues: None.
---

```python
# CASSETTE BEGINS: MESSAGE_ARDUINO
# DESCRIPTION: When a user-defined function returns a character, transmits that
# character to a connected Arduino.
# AUTHOR: Isaac Planas-Sitjà and Pranav Minasandra
# USER DEFINED VARIABLES:

# First, define a 'condition_func' function that returns either a character or None.
top = 50
right = 300
bottom = 200
left = 150

def _in_rect(locs, top=top, right=right, bottom=bottom, left=left):
    return left < locs[0,0] < right and top < locs[0,1] < bottom

def condition_func(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]
    if _in_rect(curr_loc) and not _in_rect(prev_loc):#mouse just moved into the rectangle
       return 'm'
    return None

# Then we will set up the Arduino etc.
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        manu = (port.manufacturer or "").lower()
        if 'arduino' in desc or 'arduino' in manu:
            return port.device
    raise RuntimeError('No arduino device could be found')


port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)

# Below cassette handles transmission.
@client
def message_arduino(data, clock):
    char = condition_func(data, clock)
    if char is not None:
        ser.write(bytes(char, "utf8"))

# CASSETTE ENDS: MESSAGE_ARDUINO
```
