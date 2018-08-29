import numpy as np
import cv2

def is_blue(image, noise=5):
    '''Return True if it is a blue ticket, otherwise red ticket'''
    b, g, r = cv2.split(image)
    #cv2.calcHist(images, channels, mask, histSize, ranges)
    blue_count = np.count_nonzero(b > r + noise) # sure blue
    red_count = np.count_nonzero(r > b + noise)
    return blue_count > red_count

def __region_check(roi, ratio=0.2):
    r, s = ratio, 1. - ratio
    v0, v1 = np.min(roi), np.max(roi)
    vv0 = r * v1 + s * v0
    vv1 = s * v1 + r * v0
    return np.mean(roi[np.logical_and(roi > vv0, roi < vv1)])

def is_upside_down(image, ratio=0.1):
    '''Check if the ticket is upside down,
    as the ticket may be misplaced during scanning'''
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    top_mean = __region_check(im[:50, :], ratio)
    bot_mean = __region_check(im[-50:, :], ratio)
    return top_mean < bot_mean