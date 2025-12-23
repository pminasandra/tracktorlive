"""
Real-time low-cost animal tracking system.
"""

import json
import os
from os.path import join as joinpath
import platformdirs as pfd
import pathlib
config_file = pathlib.Path.home()/".trlrc"
if not config_file.exists():
    print("rc file could not be found. This may happen if it is your first time running tracktorlive. Creating one for you at", str(config_file))
    with open(config_file, "w") as f:
        json.dump(config.settings, f, indent=2)

with open(config_file) as f:
    rcParams = json.load(f)

from .server import TracktorServer, spawn_trserver, run_trserver, close_trserver, wait_and_close_trserver, run_trsession
from .client import TracktorClient, spawn_trclient, run_trclient, close_trclient, wait_and_close_trclient, list_feeds
from .paramfixing import gui_set_params as get_params_from_gui
from . import config

__version__ = "0.9.0"
__author__ = "Pranav Minasandra, Isaac Planas-Sitja, Dominique Roche, Vivek H Sridhar"
__license__ = "MIT"
__url__ = "https://github.com/pminasandra/tracktorlive"

__all__ = ['TracktorServer', 'TracktorClient',
            'spawn_trserver', 'run_trserver', 'close_trserver',
            'spawn_trclient', 'run_trclient', 'close_trclient',
            'list_feeds', 'get_params_from_gui'
            ]

APP_NAME = "tracktorlive"
APP_AUTHOR = "Pranav Minasandra, Isaac Planas-Sitjà, Dominique Roche, Vivek H Sridhar"
FEEDS_DIR = joinpath(
                pfd.user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR),
                "LiveFeeds"
                )
CLIENTS_DIR = joinpath(
                pfd.user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR),
                "LiveClients"
                )
os.makedirs(FEEDS_DIR, exist_ok=True)
os.makedirs(CLIENTS_DIR, exist_ok=True)
#Miscellaneous
SUPPRESS_INFORMATIVE_PRINT = False

