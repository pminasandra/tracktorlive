# Pranav Minasandra, Vivek H Sridhar, and Isaac Planas-Sitja
# 15 Apr 2025
# pminasandra.github.io

"""
suite of helper functions to aid in tracking objects in video
"""

import cv2

from . import config
from . import tracktor as tr

class VideoEndedError(IOError):
    """Raised when a video has reached its end."""
    def __init__(self, message="The video has ended."):
        super().__init__(message)

def get_vid(source):
    """
    Gets a cv2.VideoCapture object from given source
    Args:
        source (int or str): filename or camera device number
    Returns:
        cv2.VideoCapture object
    """

    vidtype = "cam" if isinstance(source, int) else "file"
    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), f"could not access source {vidtype}: {source}."

    codec = config.settings['fourcc_read_codec']
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*codec))
    return cap

def get_frame(cap):
    """
    gets one frame from cap
    Args:
        cap (cv2.VideoCapture)
    Returns:
        frame, frame_index
    """

    assert cap.isOpened()
    ret, frame = cap.read()
    if not ret:
        raise VideoEndedError("frame could not be obtained")
    frame_index = cap.get(cv2.CAP_PROP_POS_FRAMES)

    return frame, frame_index


def get_contours(frame, block_size,
                 meas_last, meas_now,
                 min_area, max_area,
                 offset, scaling,
                 fps=None,
                 invert=True,
                 draw_contours=False):
    """
    Processes a video frame to detect object contours using thresholding and contour detection.

    Args:
        frame (np.ndarray): The current video frame.
        block_size (int): Size of the neighborhood for adaptive thresholding. Must be odd.
        meas_last (list): List of (x, y) coordinates from the previous frame.
        meas_now (list): List of (x, y) coordinates detected in the current frame (to be updated).
        min_area (int): Minimum area for a contour to be considered valid.
        max_area (int): Maximum area for a contour to be considered valid.
        offset (int): Offset value subtracted during adaptive thresholding.
        scaling (float): Scale factor for resizing the input frame.
        fps (float, optional): Frames per second, unused here but included for compatibility.
        invert (bool, default=True): Whether to invert the thresholded image.
        draw_contours (bool, default=False): Whether to draw detected contours on the frame.

    Returns:
        processed frame, list of contours, updated meas_last, updated meas_now
    """

    del fps
    frame = cv2.resize(frame,
                            None,
                            fx=scaling,
                            fy=scaling,
                            interpolation=cv2.INTER_LINEAR
                        )
    thresh = tr.colour_to_thresh(frame, block_size, offset, invert=invert)
    final, contours, meas_last, meas_now = tr.detect_and_draw_contours(
                                            frame,
                                            thresh,
                                            meas_last=meas_last,
                                            meas_now=meas_now,
                                            min_area=min_area,
                                            max_area=max_area,
                                            draw_contours=draw_contours
                                        )
    return final, contours, meas_last, meas_now


colours = [(0,0,255), (0,255,0), (255,0,0), (255,0,255),
                (0,255,255), (255,255,0), (0,0,0), (255,255,255)]*10

def cleanup_centroids(final, contours, n_inds,
                        meas_last, meas_now,
                        mot, frame_index,
                        draw_circles=False,
                        use_kmeans = True
                    ):
    """
    Cleans up and associates detected centroids with tracked objects using k-means and
    the Hungarian algorithm.

    Args:
        final (np.ndarray): Frame on which to draw results.
        contours (list): List of detected contours.
        n_inds (int): Number of expected individuals to track.
        meas_last (list): List of centroids from the previous frame.
        meas_now (list): List of centroids from the current frame.
        mot (bool): Whether to apply object tracking logic.
        frame_index (int): Index of the current frame (used for labeling or logging).
        draw_circles (bool, default=False): Whether to draw circles on tracked centroids.
        use_kmeans (bool, default=True): Whether to apply k-means clustering when count
                            mismatches.

    Returns:
        processed frame, updated meas_now with consistent ordering
    """

    if use_kmeans\
            and len(meas_now) != n_inds\
            and len(meas_now) > 0:

        contours, meas_now = tr.apply_k_means(contours, n_inds, meas_now)

    #if len(meas_now) == len(meas_last) and len(meas_now) > 1:
    if len(meas_now) > 0 and len(meas_last) > 0:
        _, col_ind = tr.hungarian_algorithm(meas_last, meas_now)
        final, meas_now = tr.reorder_and_draw(final, colours, n_inds,
                                                    col_ind, meas_now, mot,
                                                    frame_index,
                                                    draw_circles=draw_circles
                                                )
    return final, meas_now
