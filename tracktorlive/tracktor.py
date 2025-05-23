#!/usr/bin/env python3
# (C) Vivek Hari Sridhar, 2019
# vivekhsridhar.com
# Made free and open source under an MIT License


"""
An image-based tracking freeware designed to perform single-object tracking in
noisy environments, or multi-object tracking in uniform environments while
maintaining individual identities. Tracktor is code-based but requires no
coding skills other than the user being able to specify tracking parameters in
a designated location, much like in a graphical user interface. The
installation and use of the software is fully detailed in a user manual.

See more: https://doi.org/10.1111/2041-210X.13166
"""

#from cv2 import cv2#uncomment if you need to pylint
import cv2#comment if you need to pylint
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans

def colour_to_thresh(frame, block_size = 31, offset = 25, blur=True,
                        invert=True):
    """
    This function retrieves a video frame and preprocesses it for object
    tracking.  The code blurs image to reduce noise, converts it to greyscale
    and then returns a thresholded version of the original image.
    
    Parameters
    ---------- 
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image containing all three colour channels 
    block_size: int(optional), default = 31
        block_size determines the width of the kernel used for adaptive
        thresholding.  Note: block_size must be odd. If even integer is used,
        the programme will add 1 to the block_size to make it odd.
    offset: int(optional), default = 25 
        constant subtracted from the mean value within the block
    blur (bool): whether to blur given frame
    invert (bool): whether to invert frame color
        
    Returns
    -------
    thresh: ndarray, shape(n_rows, n_cols, 1) binarised(0,255) image
    """

    if blur:
        frame = cv2.blur(frame, (5,5))
        
    block_size |= 1

    if invert:
        threshtype = cv2.THRESH_BINARY_INV
    else:
        threshtype = cv2.THRESH_BINARY
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray,
                                    255,
                                    cv2.ADAPTIVE_THRESH_MEAN_C,
                                    threshtype,
                                    block_size,
                                    offset
                                )
    return thresh

def detect_and_draw_contours(frame, thresh, meas_last,
                                meas_now, min_area = 0, max_area=10000,
                                draw_contours=True):
    """
    This function detects contours, thresholds them based on area and draws
    them.
    
    Parameters
    ----------
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image containing all three colour channels
    thresh: ndarray, shape(n_rows, n_cols, 1)
        binarised(0,255) image
    meas_last: array_like, dtype=float
        individual's location on previous frame
    meas_now: array_like, dtype=float
        individual's location on current frame
    min_area: int
        minimum area threhold used to detect the object of interest
    max_area: int
        maximum area threhold used to detect the object of interest
    draw_contours: bool
        whether to draw detected contours on frame
        
    Returns
    -------
    final: ndarray, shape(n_rows, n_cols, 3)
        final output image composed of the input frame with object contours 
        and centroids overlaid on it if specified
    contours: list
        a list of all detected contours that pass the area based threhold
        criterion
    meas_last: array_like, dtype=float
        individual's location on previous frame
    meas_now: array_like, dtype=float
        individual's location on current frame
    """

    # Detect contours and draw them based on specified area thresholds
    if int(cv2.__version__[0]) == 3:
        _, contours, _ = cv2.findContours(thresh.copy(),
                                                    cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE
                                                )
    else:
        contours, _ = cv2.findContours(thresh.copy(),
                                                    cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE
                                                )

    final = frame.copy()

    i = 0
    if meas_last is not None:
        meas_last = meas_now[:]
        del meas_now[:]

    while i < len(contours):
        area = cv2.contourArea(contours[i])
        if min_area < area < max_area:
            if draw_contours:
                cv2.drawContours(final, contours, i, (0,0,255), 2)
            mom = cv2.moments(contours[i])
            if mom['m00']:
                cx = mom['m10']/mom['m00']
                cy = mom['m01']/mom['m00']

            if meas_last is not None:
                meas_now.append([cx,cy])
            i += 1
        else:
            contours = contours[:i] + contours[i+1:]
            
    return final, contours, meas_last, meas_now

def apply_k_means(contours, n_inds, meas_now):
    """
    This function applies the k-means clustering algorithm to separate merged
    contours. The algorithm is applied when detected contours are fewer than
    expected objects(number of animals) in the scene.
    
    Parameters
    ----------
    contours: list
        a list of all detected contours that pass the area based threhold
        criterion.
    n_inds: int
        total number of individuals being tracked
    meas_now: array_like, dtype=float
        individual's location on current frame
        
    Returns
    -------
    contours: list
        a list of all detected contours that pass the area based threhold
        criterion.
    meas_now: array_like, dtype=float
        individual's location on current frame
    """
    del meas_now[:]
    # Clustering contours to separate individuals
    myarray = np.concatenate(contours, axis=0).reshape(-1, 2)

    kmeans = KMeans(n_clusters=n_inds,
                        random_state=0,
                        n_init = 5
                    ).fit(myarray)
    l = len(kmeans.cluster_centers_)

    for i in range(l):
        x = int(tuple(kmeans.cluster_centers_[i])[0])
        y = int(tuple(kmeans.cluster_centers_[i])[1])
        meas_now.append([x,y])
    return contours, meas_now

def hungarian_algorithm(meas_last, meas_now):
    """
    The hungarian algorithm is a combinatorial optimisation algorithm used
    to solve assignment problems. Here, we use the algorithm to reduce noise
    due to ripples and to maintain individual identity. This is accomplished
    by minimising a cost function; in this case, euclidean distances between 
    points measured in previous and current step. The algorithm here is written
    to be flexible as the number of contours detected between successive frames
    changes. However, an error will be returned if zero contours are detected.
   
    Parameters
    ----------
    meas_last: array_like, dtype=float
        individual's location on previous frame
    meas_now: array_like, dtype=float
        individual's location on current frame
        
    Returns
    -------
    row_ind: array, dtype=int64
        individual identites arranged according to input ``meas_last``
    col_ind: array, dtype=int64
        individual identities rearranged based on matching locations from 
        ``meas_last`` to ``meas_now`` by minimising the cost function
    """
    meas_last = np.array(meas_last)
    meas_now = np.array(meas_now)
    if meas_now.shape != meas_last.shape:
        if meas_now.shape[0] < meas_last.shape[0]:
            while meas_now.shape[0] != meas_last.shape[0]:
                meas_last = np.delete(meas_last, meas_last.shape[0]-1, 0)
        else:
            result = np.zeros(meas_now.shape)
            result[:meas_last.shape[0],:meas_last.shape[1]] = meas_last
            meas_last = result

    meas_last = list(meas_last)
    meas_now = list(meas_now)

    cost = cdist(meas_last, meas_now)
    row_ind, col_ind = linear_sum_assignment(cost)
    return row_ind, col_ind

def reorder_and_draw(final, colours, n_inds,
                        col_ind, meas_now,
                        mot, fr_no, draw_circles=True):
    """
    This function reorders the measurements in the current frame to match
    identity from previous frame. This is done by using the results of the
    hungarian algorithm from the array col_inds.
    
    Parameters
    ----------
    final: ndarray, shape(n_rows, n_cols, 3)
        final output image composed of the input frame with object contours 
        and centroids overlaid on it
    colours: list, tuple
        list of tuples that represent colours used to assign individual
        identities
    n_inds: int
        total number of individuals being tracked
    col_ind: array, dtype=int64
        individual identities rearranged based on matching locations from 
        ``meas_last`` to ``meas_now`` by minimising the cost function
    meas_now: array_like, dtype=float
        individual's location on current frame
    mot: bool
        this boolean determines if we apply the alogrithm to a multi-object
        tracking problem
    draw_circles: bool
        whether anything should be drawn onto frames
        
    Returns
    -------
    final: ndarray, shape(n_rows, n_cols, 3)
        final output image composed of the input frame with object contours 
        and centroids overlaid on it
    meas_now: array_like, dtype=float
        individual's location on current frame
    df: pandas.DataFrame
        this dataframe holds tracked coordinates i.e. the tracking results
    """
    # Reorder contours based on results of the hungarian algorithm
    equal = np.array_equal(col_ind, list(range(len(col_ind))))
    if not equal:
        current_ids = col_ind.copy()
        reordered = [i[0] for i in sorted(enumerate(current_ids),
                                            key=lambda x:x[1]
                                        )]
        meas_now = [x for (y,x) in sorted(zip(reordered,meas_now))]

    # Draw centroids
    if not mot:
        for i in range(len(meas_now)):
            #if colours[i%4] == (0,0,255) and draw_circles:
            if draw_circles:
                cv2.circle(final, tuple((int(x) for x in meas_now[i])),
                                                            5,
                                                            colours[i%4],
                                                            -1,
                                                            cv2.LINE_AA
                                                        )
    else:
        for i in range(n_inds):
            if draw_circles:
                cv2.circle(final, tuple((int(x) for x in meas_now[i])),
                                                5,
                                                colours[i%n_inds],
                                                -1,
                                                cv2.LINE_AA
                                            )

    # add frame number
    font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    if draw_circles:
        cv2.putText(final, str(int(fr_no)), (5,30), font, 1, (255,255,255), 2)

    return final, meas_now

def reject_outliers(data, m):
    """
    This function removes any outliers from presented data.
    
    Parameters
    ----------
    data: pandas.Series
        a column from a pandas dataframe that needs smoothing
    m: float
        standard deviation cutoff beyond which, datapoint is considered as an
        outlier
        
    Returns
    -------
    index: ndarray
        an array of indices of points that are not outliers
    """
    d = np.abs(data - np.nanmedian(data))
    mdev = np.nanmedian(d)
    s = d/mdev if mdev else 0.
    return np.where(s < m)
