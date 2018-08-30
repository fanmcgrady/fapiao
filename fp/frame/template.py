import os
import importlib
import numpy as np
import cv2
import torch
import torchvision

from . import _template_match
importlib.reload(_template_match)
from ._template_match import TemplateMatch

from . import _template_associate
importlib.reload(_template_associate)
from ._template_associate import TemplateAssociate

from . import _template_cost
importlib.reload(_template_cost)
from ._template_cost import TemplateCost

from . import _template_warp
importlib.reload(_template_warp)
from ._template_warp import Warp

from . import _template_remap
importlib.reload(_template_remap)
from ._template_remap import ReMap, align_code

import fp.model.pascal_voc
importlib.reload(fp.model.pascal_voc)

import fp.core.stats
importlib.reload(fp.core.stats)


def named_rects_from_xml(xmlfile):
    '''use pascal voc as named rects'''
    objects = fp.model.pascal_voc.parse_xml(xmlfile)['objects']
    return {item['name'] : item['bndbox'] for item in objects}


class Template(object):
    '''
    template is represented by anchors
    '''
    def __init__(self, named_rects, std_size, warp_method='translate', 
                 learning_rate=0.01, max_iters=3000, debug=False):
        self.count = 1
        self.std_size = std_size
        # should be pytorch tensor
        self.names = list(named_rects.keys())
        self.aligns = list(map(align_code, named_rects.keys()))
        self.anchors = torch.stack([ReMap(align, self.std_size).to_anchor(rect) \
                                   for align, rect in zip(self.aligns, named_rects.values())])
        #print(self.anchors)
        self.center = torch.mean(self.anchors[:, :2], dim=0)
        #print(self.center)
        self.anchors[:, :2] -= self.center
        #print(self.anchors)

        #print(self.template)
        self.anchors_var = torch.tensor([[0.,0.,0.,0.]] * len(self.anchors))
        
        self.warp = Warp(warp_method)
        self.cost = TemplateCost(std_size=self.std_size)
        self.match = TemplateMatch(cost=self.cost, warp=self.warp, 
                                   learning_rate=learning_rate, iteration=max_iters, debug=debug)
        self.associate = TemplateAssociate()
        #print(self.anchors)
        #print(self.center)
        self.debug = dict() if debug else None
        if self.debug is not None:
            print('Template in debug mode')
        
    def __call__(self, detected_rects, para_init=None, update=False):
        detected_rects = torch.tensor(detected_rects).float()
        para_final, warped_abs_anchors = self.match(self.anchors, self.center, self.aligns, 
                                                detected_rects, para_init)
        
        if self.debug is not None:
            warped_rects_history = []
            for warped_abs_anchors_i in self.match.debug['warp_history']:
                warped_rects_i = torch.stack([ReMap(align, self.std_size).to_rect(anchor) \
                                             for align, anchor in zip(self.aligns, warped_abs_anchors_i)])
                warped_rects_history.append(warped_rects_i)
            self.debug['warped_rects_history'] = warped_rects_history
        
        warped_rects = torch.stack([ReMap(align, self.std_size).to_rect(anchor) \
                                   for align, anchor in zip(self.aligns, warped_abs_anchors)])
        new_rects = self.associate(warped_rects, self.aligns, detected_rects)
        new_named_rects = {name : rect for name, rect in zip(self.names, new_rects)}
        #print('new_rects:\n', new_rects)

        if update:
            # TODO: fix this
            self._update(new_rects)
            
        if self.debug is not None:
            self.debug['warped_rects'] = warped_rects
                
        return new_named_rects
                
    def _update(self, new_rects):
        assert new_rects is not None
        n_anchors = len(self.anchors)
        for j in range(n_anchors):
            new_rect = new_rects[j]
            if new_rect[2] * new_rect[3] == 0:
                continue
            new_anchor = ReMap(self.aligns[j], self.std_size).to_anchor(new_rect, False)
            for i in range(4):
                self.anchors[j, i] = fp.core.stats.online_mean(self.anchors[j, i], 
                                                               new_anchor[i], 
                                                               self.count)
                self.anchors_var[j, i] = fp.core.stats.online_var(self.anchors[j, i], 
                                                                  self.anchors_var[j, i], 
                                                                  new_anchor[i], 
                                                                  self.count)
        self.count += 1
        
