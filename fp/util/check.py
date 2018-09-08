import numpy as np
import cv2


def valid_image(im, colored=-1):
    '''
    colored : 1 must be color image
              0 must be gray image
             -1 both are ok
    '''
    assert im is not None, 'Empty image'
    assert isinstance(im, np.ndarray), 'Must be numpy array'
    if colored >= 0:
        assert len(im.shape) == 3 if colored == 1 else 2
        
def valid_rect(rect, strict=False):
    assert rect is not None
    assert len(rect) == 4
    if strict:
        assert rect[2] > 0 and rect[3] > 0
    
def valid_rects(rects, strict=False):
    assert rects is not None
    assert isinstance(rects, np.ndarray)
    assert len(rects.shape) == 2
    assert rects.shape[1] == 4
    if strict:
        for rect in rects:
            assert rect[2] > 0 and rect[3] > 0