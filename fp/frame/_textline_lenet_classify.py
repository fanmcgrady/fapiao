import os
import sys
import importlib
import numpy as np
import matplotlib.pyplot as pl
import cv2
import torch
import torchvision

from ..model import lenet
importlib.reload(lenet)

import fp.config

def sampling(image, rect):
    rx, ry, w, h = rect
    im = image[ry:ry+h, rx:rx+w]
    if h < w:
        x = np.random.randint(w - h)
        sub_im = im[0:h, x:x+h]
    elif h > w:
        y = np.random.randint(h - w)
        sub_im = im[y:y+w, 0:w]
    else:
        sub_im = im
    sub_im = cv2.resize(sub_im, (28, 28))
    sub_im = sub_im.astype(np.float32) / 255. - 0.5
    sub_im = np.expand_dims(sub_im, axis=0)
    sub_im = np.expand_dims(sub_im, axis=0)
    return sub_im

class TextlineLenetClassify(object):
    def __init__(self, weight_file=fp.config.TEXTLINE_CLASSIFY_LENET_WEIGHT):
        '''
        '''
        if fp.config.TEXTLINE_CLASSIFY_CUDA and torch.cuda.is_available():
            self.device = torch.device('cuda')
            _state_dict = torch.load(weight_file, map_location='cuda')
        else:
            self.device = torch.device('cpu')
            _state_dict = torch.load(weight_file, map_location='cpu')
        self.net = lenet.LeNet().to(self.device)
        self.net.load_state_dict(_state_dict)
    
    def __call__(self, image, rects):
        '''d'''
        types = np.zeros((len(rects),), np.uint8)
        for i, rect in enumerate(rects):
            sub_im = sampling(image, rect)
            pred = self.net(torch.from_numpy(sub_im).to(self.device))
            types[i] = 0 if torch.argmax(pred).item() == 0 else 1
        return types