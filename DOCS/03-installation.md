# Installation

TracktorLive is installable via pip and brings in all Python
dependencies automatically. However, you’ll need some basic system tools (like
compilers and build tools) installed to support underlying libraries such as
OpenCV. 

**Note:** If you're looking to contribute as a developer for this software,
please instead see the installation instructions [here](./DEV.md)

Below are platform-specific setup instructions.

### 🐧 Linux (Debian/Ubuntu)

1. Update and upgrade system packages

    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```

2. Install development tools

    ```bash
    sudo apt install -y build-essential cmake make flex bison lld python3-dev
    ```

3. Ensure Python and pip are available

    ```bash
    sudo apt install -y python3 python3-pip python3-setuptools python3-wheel
    ```

4. Install Tracktorlive

    ```bash
    python -m pip install tracktorlive
    ```

(you might need to use `python3` instead of `python` based on your
installation.)

**Note:** If you get an error complaining of an 'externally managed
environment', you should try to set up a `venv` environment to handle the
installation. Another, slightly riskier workaround is to install with the
break system packages flag:

```bash
python -m pip install tracktorlive --break-system-packages
```

Needless to say, with this option you run the risk of breaking your system
packages. However, it has worked flawlessly so far on both normal Linux and WSL
installs.

### 🍎 macOS

1. Install Homebrew (if not already installed):

    ```bash 
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. Install system tools and python

    ```bash 
    brew install cmake make flex bison lld
    brew install python
    ```

3. Install TracktorLive

    ```bash
    pip3 install tracktorlive
    ```





### 🪟 Windows (via WSL)

> TracktorLive is designed for Linux-like environments. Windows users should
> install WSL (Windows Subsystem for Linux, see below).

1. Install WSL (Windows 10 and 11 only). Open the pre-installed software
   'Powershell', and run:

    ```powershell
    wsl --install -d Ubuntu
    ```

    You might be prompted to enter a username and password for the virtual Linux
    system, which you will need to remember.
    Restart your computer after this step finishes.

2. After restarting, start WSL on Powershell

    ```powershell
    wsl
    ```

3. You are now within WSL in a 'bash' shell. Run

    ```bash
    cd ~
    ```

    to enter your Linux home directory.

4. To get access to GUI functionality on WSL, e.g., for fixing parameter values,
    and to fully update the virtual linux system,
    run the following commands within WSL.

    ```bash
    sudo apt update
    sudo apt upgrade -y
    sudo apt install vlc -y
    sudo apt install python3-pyqt5 python3-opencv libxcb-xinerama0 -y
    ```

    **Note**: The GUI might not work on outdated versions of WSL.

5. Follow Linux instructions (above) for further proceedings.

6. Run all TracktorLive scripts within WSL.

**NOTE 1**: A basic knowledge of Linux shell commands can help you be comfortable
with WSL, and in executing scripts. You can familiarise yourself with these
systems in a fairly short time, should you choose to do so. We recommend Will
Shotts' [The Linux Command Line](https://linuxcommand.org/tlcl.php), a free
resource, for this purpose.

**NOTE 2**: WSL users have to follow additional steps to allow the virtual
system to access web-cams and Arduino devices. You can go [here](COMPORT.md) to
read instructions for this.

[previous](02-quickstart.md) | [next](04-cli.md)

