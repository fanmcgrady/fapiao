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
    def __init__(self, weights=[0.3, 0.4, 0.1, 0.2]):
        self.weights = torch.tensor(weights)

    def __call__(self, abs_anchors, aligns, detected_candidates):
        '''
        template must be a dict with float tensor value
        '''
        detected_anchors_l = detected_candidates[0]
        detected_anchors_c = detected_candidates[1]
        detected_anchors_r = detected_candidates[2]

        total_cost = []
        for align, abs_anchor in zip(aligns, abs_anchors):
            if align == remap.LEFT:
                detected_anchors = detected_anchors_l
            elif align == remap.RIGHT:
                detected_anchors = detected_anchors_r
            else:
                detected_anchors = detected_anchors_c
            cost = self._min_dist_cost(abs_anchor, detected_anchors)
            total_cost.append(cost)
        total_cost = torch.stack(total_cost)
        return torch.mean(total_cost)

    def _min_dist_cost(self, abs_anchor, detected_anchors):
        n_repeat = len(detected_anchors)
        repeat_abs_anchors = torch.stack([abs_anchor] * n_repeat, dim=0)
        sqr_diff = (repeat_abs_anchors - detected_anchors) ** 2
        matches = torch.matmul(sqr_diff, self.weights)
        match_min, _ = torch.min(matches, dim=0)
        return match_min