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


class Detect(object):
    '''Textline Detect'''
    default_pars_simple = dict()
    default_pars_textboxes = dict()

    def __init__(self, method='simple', pars={}):
        if method == 'simple':
            self.detect = TextlineSimpleDetect(**pars)
        elif method == 'textboxes':
            self.detect = TextlineTextBoxesDetect(**pars)
        else:
            raise NotImplemented
    
    def __call__(self, image):
        '''
        return list of rects'''
        return self.detect(image)
    
def visualize_detect(image, rects):
    return fp.core.draw.rects(image, rects)

    
class Classify(object):
    '''Textline Detect'''
    default_pars_lenet = dict(weight_file=fp.config.TEXTLINE_CLASSIFY_LENET_WEIGHT)
    
    def __init__(self, method='lenet', pars=default_pars_lenet):
        if method == 'lenet':
            self.classify = TextlineLenetClassify(**pars)
        else:
            raise NotImplemented
    
    def __call__(self, image, rects):
        return self.classify(image, rects)