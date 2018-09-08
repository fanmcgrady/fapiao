import importlib
import numpy as np
import cv2

from ..core import quad
importlib.reload(quad)
from ..core import trans
importlib.reload(trans)
from ..core import line
importlib.reload(line)

from . import _surface_check
importlib.reload(_surface_check)
from ._surface_check import is_crop_ready

import fp.util.check
importlib.reload(fp.util.check)

class Find(object):
    '''find rects in image'''
    def __init__(self):
        self.approx_ratio = 0.02
        self.min_area = 60
        
    def __call__(self, mask):
        quads, conts = quad.find_quads(mask, approx_ratio=self.approx_ratio, 
                                       min_area=self.min_area)
        if len(conts) == 0:
            return None, None
        boxes = [cv2.minAreaRect(cont) for cont in conts]
        areas = [box[1][0] * box[1][1] for box in boxes]
        idx = np.argmax(areas)
        
        # rotate 90-degree if width-height are reversed
        box = list(boxes[idx])
        box[0], box[1] = list(box[0]), list(box[1])
        if box[1][0] < box[1][1]:
            box[1][0], box[1][1] = box[1][1], box[1][0]
            box[2] += 90.0
            if box[2] >= 360.0:
                box[2] -= 360.0
        return quads[idx], box

class Crop(object):
    def __init__(self, method=None, pars=None):
        pass
    
    def __call__(self, image, box):
        center, dsize, angle = box
        dsize = int(dsize[0]), int(dsize[1])
        return trans.rotate_crop(image, center, angle, dsize)

def _restore_box(box, fx):
    ifx = 1. / fx
    center, dsize, angle = box
    center = ifx * center[0], ifx * center[1]
    dsize = ifx * dsize[0], ifx * dsize[1]
    return center, dsize, angle

class Adjust(object):
    def __init__(self, line_length_ratio=0.2):
        self.lsd = cv2.createLineSegmentDetector()
        self.th_ratio = 0.8
        # assumed: max(detected_line_length) > min(w, h) * line_length_ratio
        self.line_length_ratio = line_length_ratio
        
    def __call__(self, std_im):
        assert std_im is not None, 'Empty image'
        assert isinstance(std_im, np.ndarray), 'Must numpy'
        assert len(std_im.shape) == 3, 'Must color'
        im = cv2.cvtColor(std_im, cv2.COLOR_BGR2GRAY)
        lines0 = self._detect_region(im[:40, :])
        lines1 = self._detect_region(im[-40:, :])
        lines = np.concatenate((lines0, lines1))
        
        max_line_len = np.max(list(map(line.line_length, lines)))
        ref_size = np.min(std_im.shape[:2])
        if max_line_len < self.line_length_ratio * ref_size:
            return std_im
        line_lens_th = max_line_len * self.th_ratio
        strong_lines = list(filter(lambda x : line.line_length(x) > line_lens_th, lines))
        line_angs = np.array(list(map(line.line_angle, strong_lines)))
        line_lens = np.array(list(map(line.line_length, strong_lines)))
        ang = np.sum(line_angs * line_lens) / np.sum(line_lens)
        h, w = std_im.shape[:2]
        im_ft = trans.rotate_crop(std_im, center=(w/2, h/2), angle=ang, dsize=(w,h), 
                                  border_color=(255,255,255))
        return im_ft
        
    def _detect_region(self, sub_im):
        _lines, width, prec, nfa = self.lsd.detect(sub_im)
        _lines = np.squeeze(_lines)
        return _lines

class Detect(object):
    def __init__(self, aspect_ratio_th=0.5, adjust_pars={}, debug=False):
        '''
        aspect_ratio < _th : roll-ticket (thin)
                     > _th : other ticket or invoice (fat)
        '''
        self.std_size = 400
        self.find_frame = Find()
        self.crop_frame = Crop()
        self.adjust = Adjust(**adjust_pars)
        self.aspect_ratio_th = aspect_ratio_th
        self.debug = dict() if debug else None
        
    def __call__(self, image):
        # check input
        fp.util.check.valid_image(image, colored=1)
        
        # if image is cropped, just return
        if not is_crop_ready(image):
            std_image = self._detect(image)
            if std_image is None:
                return None
        else:
            std_image = image
        
        std_image = self.adjust(std_image)
        if self._is_misorient(std_image):
            std_image = np.rot90(std_image, k=1, axes=(0, 1))
        return std_image
    
    def _detect(self, image):
        fx = 1. * self.std_size / np.min(image.shape[:2])
        im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im = cv2.resize(im, None, fx=fx, fy=fx)
        im = cv2.GaussianBlur(im, (3,3), 1.2)
        if self.debug is not None:
            self.debug['image'] = im
            
        max_pix = np.max(im)
        _, mask = cv2.threshold(im, max_pix-2, 255, cv2.THRESH_BINARY_INV)
        if self.debug is not None:
            self.debug['mask'] = mask
            
        quad, box = self.find_frame(mask)
        if self.debug is not None:
            self.debug['quad'] = quad
            self.debug['box'] = box
            
        if box is None:
            return None
        box = _restore_box(box, fx)
        box_im = self.crop_frame(image, box)
        
        return box_im
        
    def _is_misorient(self, std_image):
        h, w = std_image.shape[:2]
        aspect_ratio = min(h, w) / max(h, w)
        # Fat and h>w, or Thin and h<w
        return (aspect_ratio > self.aspect_ratio_th) == (h > w)
    

            
    