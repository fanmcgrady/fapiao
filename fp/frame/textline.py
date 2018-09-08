import os
import importlib
import numpy as np
import cv2

import fp.config
importlib.reload(fp.config)

from . import _textline_simple_detect
importlib.reload(_textline_simple_detect)
from ._textline_simple_detect import TextlineSimpleDetect

from . import _textline_lenet_classify
importlib.reload(_textline_lenet_classify)
from ._textline_lenet_classify import TextlineLenetClassify

import fp.util.check
importlib.reload(fp.util.check)


class Detect(object):
    '''Textline Detect'''
    default_pars_simple = dict()
    default_pars_textboxes = dict()

    def __init__(self, method='simple', pars={}, debug=False):
        if method == 'simple':
            self.detect = TextlineSimpleDetect(**pars, debug=debug)
        elif method == 'textboxes':
            self.detect = TextlineTextBoxesDetect(**pars, debug=debug)
        else:
            raise NotImplemented
    
    def __call__(self, image):
        '''
        return list of rects'''
        fp.util.check.valid_image(image, colored=0)
        return self.detect(image)

    
class Classify(object):
    '''Textline Detect'''
    default_pars_lenet = dict(weight_file=fp.config.TEXTLINE_CLASSIFY_LENET_WEIGHT)
    
    def __init__(self, method='lenet', pars=default_pars_lenet):
        if method == 'lenet':
            self.classify = TextlineLenetClassify(**pars)
        else:
            raise NotImplemented
    
    def __call__(self, image, rects):
        fp.util.check.valid_image(image, colored=0)
        fp.util.check.valid_rects(rects)
        return self.classify(image, rects)