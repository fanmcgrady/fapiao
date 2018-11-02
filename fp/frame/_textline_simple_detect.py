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
        image[y: y + h, x: x + w] = 255
    return image

class TextlineSimpleDetect(object):
    '''Simple Textline Detector Based on Connected Component'''

    def __init__(self, std_image_size=None,
                 thresh_pars=dict(mix_ratio=0.2, rows=4, cols=6, ksize=11, c=3),
                 char_expand_ratio=1.5, textline_shrink_ratio=0.4,
                 char_size_range=(14, 60, 14, 60), textline_rule=None, debug=False):
        self.std_image_size = std_image_size
        self.char_expand_ratio = char_expand_ratio  # relative to char width
        self.textline_shrink_ratio = textline_shrink_ratio  # relative to textline height
        self.char_size_range = char_size_range
        self.textline_rule = textline_rule
        self.threshold = thresh.HybridThreshold(**thresh_pars)
        self.debug = dict() if debug else None

    def __call__(self, image):
        inv_fx, inv_fy = 1.0, 1.0
        if self.std_image_size is not None:
            inv_fx = image.shape[1] / self.std_image_size[0]
            inv_fy = image.shape[0] / self.std_image_size[1]
            image = cv2.resize(image, self.std_image_size)
        h, w = image.shape[:2]
        raw_segm_im = self.threshold(image)
        if self.debug is not None:
            self.debug['binary'] = raw_segm_im

        ##############
        # find chars
        ##############
        _, contours, _ = cv2.findContours(255 - raw_segm_im, mode=cv2.RETR_LIST,
                                          method=cv2.CHAIN_APPROX_SIMPLE)

        char_rects = map(cv2.boundingRect, contours)
        char_rects = filter(self._is_char, char_rects)
        char_rects = np.array(list(map(self._expand_char_rect, char_rects)))
        if self.debug is not None:
            self.debug['char_rects'] = char_rects

        #################
        # find textline
        #################
        char_rects_im = make_rects_mask(image.shape, char_rects)
        if self.debug is not None:
            self.debug['char_mask'] = char_rects_im.copy()
        _, contours, _ = cv2.findContours(char_rects_im.copy(), mode=cv2.RETR_LIST,
                                          method=cv2.CHAIN_APPROX_SIMPLE)

        textline_rects = map(cv2.boundingRect, contours)
        # if self.debug is not None:
        #    self.debug['textline_rects0'] = np.array(list(textline_rects))
        textline_rects = filter(self._is_textline, textline_rects)
        textline_rects = map(self._shrink_textline_rect, textline_rects)
        textline_rects = np.array(list(textline_rects), dtype=np.float32)
        if self.std_image_size is not None:
            textline_rects[:, 0::2] *= inv_fx
            textline_rects[:, 1::2] *= inv_fy
            textline_rects = np.round(textline_rects).astype(np.int64)
        if self.debug is not None:
            self.debug['textline_rects'] = textline_rects
        return textline_rects

    def _expand_char_rect(self, rect):
        x, y, w, h = rect
        cw0, cw1, ch0, ch1 = self.char_size_range
        # new_x = int(x - round(w * self.char_expand_ratio / 2))
        #new_w = int(w + round(w * self.char_expand_ratio))
        s = int(max(w, h) * 0.5 + 0.5 * (cw0 + cw1) / 2)
        new_x = int(x - round(s * self.char_expand_ratio / 2))
        new_w = int(w + round(s * self.char_expand_ratio))
        return new_x, y, new_w, h

    def _shrink_textline_rect(self, rect):
        x, y, w, h = rect
        new_x = int(x + round(h * self.textline_shrink_ratio / 2))
        new_w = int(w - round(h * self.textline_shrink_ratio))
        return new_x, y, new_w, h

    def _is_char(self, rect):
        '''todo improve this'''
        x, y, w, h = rect
        cw0, cw1, ch0, ch1 = self.char_size_range
        if not _in_range(w, 0, cw1):
            return False
        if not _in_range(h, 0, ch1):
            return False
        return True

    def _is_textline(self, rect):
        x, y, w, h = rect
        cw0, cw1, ch0, ch1 = self.char_size_range
        if not _in_range(h, ch0, 1.5 * ch1):
            return False
        elif h > 2 * w:
            return False
        elif w * h < 2 * cw0 * ch0:
            return False
        else:
            return True
