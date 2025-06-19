# Pranav Minasandra
# 17 June 2025
# pminasandra.github.io

import json
from pathlib import Path

defaults = {
    'fourcc_read_codec': 'YUYV',
    'file_format': 'avi'
}

config_file = Path.home()/".trlrc"
if config_file.exists():
    with open(config_file) as f:
        settings = json.load(f)
    for s in defaults:
        if s not in settings:
            settings[s] = defaults[s]
else:
    settings = defaults
