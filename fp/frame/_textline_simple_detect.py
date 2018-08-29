import os
import importlib
import numpy as np
import cv2

from ..core import thresh
importlib.reload(thresh)


def _in_range(x, x0, x1):
    return x0 <= x <= x1

def make_rects_mask(mask_shape, rects):
    image = np.zeros(mask_shape, np.uint8)
    for x, y, w, h in rects:
        image[y : y + h, x : x + w] =  255
    return image

class TextlineSimpleDetect(object):
    '''Simple Textline Detector Based on Connected Component'''
    def __init__(self, std_image_size=None, thresh_grid_shape=(4, 6), 
                 char_expand_ratio=1.0, textline_shrink_ratio=0.4,
                 char_size_range=(0,100,0,100), textline_rule=None):
        self.std_image_size = std_image_size
        self.thresh_grid_shape = thresh_grid_shape
        self.char_expand_ratio = char_expand_ratio          # relative to char width
        self.textline_shrink_ratio = textline_shrink_ratio  # relative to textline height
        self.char_size_range = char_size_range
        self.textline_rule = textline_rule
    
    def __call__(self, image):
        if self.std_image_size is not None:
            image = cv2.resize(image, self.std_image_size)
        h, w = image.shape
        raw_segm_im = thresh.adaptive_otsu(image, *self.thresh_grid_shape) #
        self.raw_segm = raw_segm_im
        
        ##############
        # find chars
        ##############
        _, contours, _ = cv2.findContours(255 - raw_segm_im, mode=cv2.RETR_LIST, 
                                          method=cv2.CHAIN_APPROX_SIMPLE)
        
        char_rects = map(cv2.boundingRect, contours)
        char_rects = filter(self._is_char, char_rects)
        char_rects = map(self._expand_char_rect, char_rects)
        self.char_rects = np.array(list(char_rects))
        
        #################
        # find textline
        #################
        char_rects_im = make_rects_mask(image.shape, self.char_rects)
        _, contours, _ = cv2.findContours(char_rects_im.copy(), mode=cv2.RETR_LIST, 
                                          method=cv2.CHAIN_APPROX_SIMPLE)
        
        textline_rects = map(cv2.boundingRect, contours)
        textline_rects = filter(self._is_textline, textline_rects)
        textline_rects = map(self._shrink_textline_rect, textline_rects)
        self.textline_rects = np.array(list(textline_rects))
        return self.textline_rects
        
    def _expand_char_rect(self, rect):
        x, y, w, h = rect
        new_x = int(x - round(w * self.char_expand_ratio / 2))
        new_w = int(w + round(w * self.char_expand_ratio))
        return new_x, y, new_w, h
        
    def _shrink_textline_rect(self, rect):
        x, y, w, h = rect
        new_x = int(x + round(h * self.textline_shrink_ratio / 2))
        new_w = int(w - round(h * self.textline_shrink_ratio))
        return new_x, y, new_w, h
    
    def _is_char(self, rect):
        '''todo improve this'''
        x, y, w, h = rect
        w0, w1, h0, h1 = self.char_size_range
        if not _in_range(w, w0, w1):
            return False
        if not _in_range(h, h0, h1):
            return False
        return True
    
    def _is_textline(self, rect):
        x, y, w, h = rect
        if h < 10 or h > 2*w or w < 10:
            return False
        else:
            return True