# Pranav Minasandra
# 17 Apr 2025
# pminasandra.github.io

"""
Utilities for shared memory handling and associated stuff
"""

import multiprocessing.shared_memory as mpshm

def create_shared_data(size):
    """
    Deals with the creation and setup of a shared memory object.
    """
    shm = mpshm.SharedMemory(create=True, size=size)
    return shm
