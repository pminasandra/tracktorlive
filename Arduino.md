# How to use TracktorLive with Arduino

## What is Arduino?
[Arduino](https://www.arduino.cc/) is an open-source electronics platform based on easy-to-use hardware and software. It consists of a microcontroller board (such as the Arduino Uno) and the Arduino IDE, which allows users to write and upload code to the board.
Designed for both beginners and professionals, Arduino enables the creation of interactive electronic projects. For example, you can connect TracktorLive to an Arduino to trigger actions or control devices when an animal enters a specific area.
As an open-source project, both the hardware schematics and the software tools are freely available (click [here](https://docs.arduino.cc/) for more online documentation). There is also a large, active community that offers free tutorials, examples, libraries, and troubleshooting help online.

## How Arduino Works
An Arduino board operates by reading input (e.g. light from a sensor or a button press) and converting it into output (e.g. turning on an LED or activating a motor). The logic is written in C/C++ using the Arduino IDE and uploaded to the board via USB. Once uploaded, the board executes the code autonomously.
Thanks to its versatility, Arduino is especially useful in real-time tracking applications—such as automating data collection or triggering mechanical devices in behavioural experiments.


## Step-by-step guide

### 1. Install Arudino Arduino Integrated Development Environment (IDE) on your computer. 
More information here: https://docs.arduino.cc/software/ide/#ide-v2 (choose ide-v1 or ide-v2)

### 2. Sketching

Programs created with the Arduino IDE are known as sketches and use the .ino file extension. The IDE provides a straightforward text editor for writing and managing code, with standard tools like cut, paste, search, and replace. Feedback during saving, compiling, or uploading appears in the message area, while the console below shows detailed outputs, such as errors and messages from the board. The lower right corner indicates which board and serial port are currently selected. A set of toolbar buttons makes it easy to verify, upload, and manage sketches, as well as access the Serial Monitor for real-time data from the board.

Arduino programs are written in a simplified version of C/C++ and follow a basic structure composed of two main functions: ```setup()``` and ```loop()```.

```
setup()
```
This function runs once when the Arduino board is powered on or reset. It's used to initialise settings, such as pin modes (input or output), start serial communication, or set initial states for components. For example:

```
void setup() {
  pinMode(13, OUTPUT); // Set digital pin 13 as an output
}

```
The ```//``` are used to add comments, and each line needs to end with a ```;```. 

```
loop()
```
This function runs continuously in a cycle after ```setup()``` finishes. This is where the main logic of your program goes—for example, reading sensor values, responding to inputs, or updating outputs. For example:

```
void loop() {
  digitalWrite(13, HIGH); // Turn the LED on
  delay(1000);            // Wait for one second
  digitalWrite(13, LOW);  // Turn the LED off
  delay(1000);            // Wait for one second
}
```

Together, these two functions define how the Arduino behaves. 

### 3. Connect Arduino board to a USB port and upload the code.

To upload code to your Arduino, first connect the board to your computer using the USB cable. The Arduino IDE should automatically detect the board’s presence.

*Select the Board:* In the Arduino IDE, go to *Tools* > *Board* and choose the exact model of your Arduino (e.g., Arduino Uno).

*Select the Port:* Under *Tools* > *Port*, select the serial port that corresponds to your Arduino. This is usually labelled something like COM3 on Windows or /dev/ttyUSB0 or /dev/ttyACM0 on Linux/macOS.

*Upload Your Sketch:* Click the Upload button (right arrow icon) in the IDE. The code will be compiled and sent to the board via USB. The board’s onboard LED will typically blink during this process.

*If the board is not detected or upload fails, check your USB connection, verify the correct board and port are selected, and ensure drivers (if needed) are installed.*

Uploading this code to the board via USB using the Arduino IDE will allow the microcontroller to execute this code autonomously.

## Linking Tracktorlive with Arduino

To link the real-time detection of the TracktorLive to the Arduino, we use the Serial Monitor. As an overview, we implement a cassette in TracktorLive that sends a message to the Serial Monitor when we detect a specific event (i.e., individual enters a specific area, or two individuals are close proximity), and we program the Arduino to execute an action when it receives this message. 

Here below, we provide an example on how to turn on an LED light when the focus individual enters a circular area of interst (ROI). For more information on how to define ROI or establish a connection between TracktorLive and Arduino, please see *Cassettes Library* > *Arduino section*.

**1. Python script**

We can use this Python script to run TracktorLive and track our focus individual:

```
import json
import multiprocessing as mp
mp.set_start_method('fork')

import cv2
import serial
import serial.tools.list_ports
import numpy as np

import tracktorlive as trl

# 1. This cassette is used to automatically detect the USB port connected to the Arduino.
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        manu = (port.manufacturer or "").lower()
        if 'ttyUSB' in port.device or 'ser' in desc or 'arduino' in manu or 'arduino' in desc:
            return port.device
    raise RuntimeError('No arduino device could be found')

# 2. Make sure port is detected:

port = find_arduino_port()
ser = serial.Serial(port, 9600, timeout=1)

# 3. Load parameters for tracking
with open("insects.json") as f:
    params = json.load(f)
params["fps"] = 30

server, semm = trl.spawn_trserver(4,
                                params=params,
                                n_ind = 1,
                                realtime=True,
                                buffer_size = 1,
                                draw=True,
                                feed_id="insectinthehouse"
                            )

# 3. Define circle ROI parameters, and draw circle on the overlay
center = (268, 167)  # Centre of the circle
radius = 45          # Radius of the circle
color = (0, 255, 0)  # Green
alpha = 0.5          # Transparency factor

@server
def show(server):
    if server.framesbuffer[-1] is None:
        return None
    fr = server.framesbuffer[-1].copy()
    fr2 = fr.copy()
    # Draw filled circle on fr
    cv2.circle(fr, center, radius, color, thickness=-1)
    # Blend the circle onto the frame
    cv2.addWeighted(fr, alpha, fr2, 1 - alpha, 0, fr2)
    cv2.imshow('tracking', fr2)
    cv2.waitKey(1)

client = trl.spawn_trclient("insectinthehouse")


# 4. Cassette to detect individual inside the circle

def _in_circle(locs, center=center, radius=radius):
    # Calculate the distance from locs to the circle center
    distance = np.sqrt((locs[0, 0] - center[0])**2 + (locs[0, 1] - center[1])**2)
    return distance < radius

# 5. Launch cassette to send a message to Serial Monitor
@client
def send_to_arduino(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]

    if _in_circle(curr_loc) and not _in_circle(prev_loc):#animal just moved into the circle
           ser.write(b'm')

# 6. End script
trl.run_trsession(server, semm, client)
del client
del server
```

In the Python script above, we can see the section 5 is the one communicating with the Serial Monitor of the Arduino board:

```
@client
def send_to_arduino(data, clock):
    curr_loc = data[:,:,-1]
    prev_loc = data[:,:,-2]

    if _in_circle(curr_loc) and not _in_circle(prev_loc):#animal just moved into the circle
           ser.write(b'm')
```

This cassette sends a message ```m``` when the individual moves into the ROI, and we can detect so by using the ```_in_circle()``` function.

**2. Arduino sketch**

If we want to turn on a LED when the individual enters the ROI, our sketch (```.ino``` file) would look like this:

```
/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products
  https://www.arduino.cc/en/Tutorial/BuiltInExamples/Blink
*/

char c;
// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(9600);
}

// the loop function runs over and over again forever
void loop() {
  // if we receive communication from user
  if (Serial.available() > 0) {
    // read what we receive
    c = Serial.read();
    // if it's our code, we activate heron 
    if (c == 'm') {
      digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
      delay(500);
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}
```
This Arduino sketch above listens for serial input and activates the built-in LED when a specific character ('m') is received.

```char c;``` declares a character variable to store incoming serial data.

```setup()``` runs once when the board is powered on or reset to: set the built-in LED pin as an output, turn the LED off initially, start serial communication at 9600 baud.

```loop()``` runs repeatedly. It checks if data is available from the serial port, and reads the incoming character. If the character is 'm', it turns on the built-in LED for 500 milliseconds, then turns it off.
