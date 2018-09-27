import numpy as np
import cv2


def valid_image(im, colored=-1):
    '''
    colored : 1 must be color image
              0 must be gray image
             -1 both are ok
    '''
    if im is None:
        return False
    if not isinstance(im, np.ndarray):
        return False
    if colored >= 0:
        if not (len(im.shape) == 3 if colored == 1 else 2):
            return False
    return True
        
def valid_rect(rect, strict=False):
    if rect is None:
        return False
    if len(rect) != 4:
        return False
    if strict:
        if rect[2] < 0 or rect[3] < 0:
            return False
    return True
    
def valid_rects(rects, strict=False):
    if rects is None:
        return False
    if not isinstance(rects, np.ndarray):
        return False
    if len(rects.shape) != 2:
        return False
    if rects.shape[1] != 4:
        return False
    if strict:
        for rect in rects:
            if rect[2] < 0 or rect[3] < 0:
                return False
    return True


def valid_size(size):
    if size is None:
        return False
    if len(size) != 2:
        return False
    if size[0] < 0 or size[1] < 0:
        return False
    return True
