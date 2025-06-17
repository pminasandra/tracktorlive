---
title: Adding USB port devices on WSL
author: Pranav Minasandra
---

# Adding devices like Web-cam and Arduino on WSL

**Note to self:** Eventually fold this into a larger TROUBLESHOOTING.md that is better
written.

**Note:** This document applies to Windows users using WSL. Webcam and Arduino
are not easy to access with WSL right now, requiring a few additional steps.
I try here to give you a quick run-down on how to go about doing this. I am
assuming you have already followed the instructions in [DOCS.md](DOCS.md) to
install and set-up WSL.

## 1. Bind and attach your device to a WSL session.

Follow the instructions [here](https://learn.microsoft.com/en-us/windows/wsl/connect-usb), that use the software USBIPD, to tell Windows to
share its USB devices (which include on-board Webcam, USB Webcam, Arduino, etc)
with the running virtual WSL session. 

## 2. Give your Linux username permission to access these devices.

If you are trying to access a webcam, you need to be added to the group `video`.
If you need to access an Arduino, you need to be in the group `dialout`.

First, run the command

```bash
sudo usermod -aG <groupname> <username>
```

where `<groupname>` is `video` or `dialout` as mentioned above, and `<username>`
is your WSL username.

## 3. Webcam configuration.

Run `tracktorlive gui --camera 0`. If a window opens but fails to show any
video, you have a minor problem. Open the file `.trlrc` that tracktorlive
creates by default in your home directory on Linux, and replace the string
'YUYV' with the string 'MJPG'. In our experience this is enough to access the
webcam.
