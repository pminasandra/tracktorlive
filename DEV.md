
# Help for developers

## Installing from GitHub

**Note:** I have used the command `python` below, but most likely, depending on
your installation, you need to use `python3` in place of `python`.

1. To develop this software, you need to first uninstall the current version of
   TracktorLive installed on your system.

   ```bash
   python -m pip uninstall tracktorlive
   ```

2. Clone this repository

   ```bash
   git clone https://github.com/pminasandra/tracktorlive
   ```

3. Enter the directory and make an 'editable' installation

   ```bash
   cd tracktorlive
   python -m pip install --user --editable .
   ```

Now, you can use tracktorlive as a library anywhere while continuing to edit the
library itself in your cloned repository.
