'''
* to find a best init state
'''

import os
import importlib
import numpy as np
import cv2
import torch
import torchvision

from . import _template_remap as remap
importlib.reload(remap)

class TemplateCost(object):
    def __init__(self, std_size, weights=[0.3, 0.4, 0.1, 0.2]):
        assert len(std_size) == 2
        self.std_size = std_size
        self.weights = torch.tensor(weights)
        
    def __call__(self, abs_anchors, aligns, detect_rects):
        '''template must be a dict with float tensor value'''
        xl, xc, xr, yc, w, h = self._anchor_candiates(detect_rects)
        detect_abs_anchors_l = torch.stack((xl, yc, w, h), dim=1)
        detect_abs_anchors_c = torch.stack((xc, yc, w, h), dim=1)
        detect_abs_anchors_r = torch.stack((xr, yc, w, h), dim=1)

        total_cost = []
        for align_code, abs_anchor in zip(aligns, abs_anchors):
            if align_code == remap.LEFT:
                detect_abs_anchors = detect_abs_anchors_l
            elif align_code == remap.RIGHT:
                detect_abs_anchors = detect_abs_anchors_r
            else:
                detect_abs_anchors = detect_abs_anchors_c
            cost = self._min_dist_cost(abs_anchor, detect_abs_anchors)
            total_cost.append(cost)
        total_cost = torch.stack(total_cost)
        return torch.mean(total_cost)
    
    def _min_dist_cost(self, abs_anchor, detect_abs_anchors):
        n_repeat = len(detect_abs_anchors)
        repeat_abs_anchors = torch.stack([abs_anchor] * n_repeat, dim=0) 
        sqr_diff = (repeat_abs_anchors - detect_abs_anchors)**2
        matches = torch.matmul(sqr_diff, self.weights)
        match_min, _ = torch.min(matches, dim=0)
        return match_min

    def _anchor_candiates(self, detect_rects):
        x, y = detect_rects[:, 0], detect_rects[:, 1]
        w, h = detect_rects[:, 2], detect_rects[:, 3]
        xl = (x) / self.std_size[0]
        xc = (x + w / 2) / self.std_size[0]
        xr = (x + w) / self.std_size[0]
        yc = (y + h / 2) / self.std_size[1]
        w_ = w / self.std_size[0]
        h_ = h / self.std_size[1]
        return xl, xc, xr, yc, w_, h_