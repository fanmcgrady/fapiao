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

import fp.util.check
importlib.reload(fp.util.check)

def named_rects_from_xml(xmlfile):
    '''use pascal voc as named rects'''
    objects = fp.model.pascal_voc.parse_xml(xmlfile)['objects']
    return {item['name'] : item['bndbox'] for item in objects}

def _vector_update(vec_mean, vec_var, new_vec, count):
    assert len(vec_mean) == len(vec_var) and len(vec_mean) == len(new_vec)
    for i in range(len(vec_mean)):
        vec_mean[i] = fp.core.stats.online_mean(vec_mean[i], new_vec[i], count)
        vec_var[i] = fp.core.stats.online_var(vec_mean[i], vec_var[i], new_vec[i], count)


class Template(object):
    '''
    template is represented by anchors
    '''
    def __init__(self, named_rects, std_size, warp_method='translate', 
                 learning_rate=0.01, max_iters=3000, debug=False):
        self.count = 1
        self.std_size = std_size
        
        self.names = list(named_rects.keys())
        self.aligns = list(map(align_code, named_rects.keys()))
        # should be pytorch tensor
        self.center, self.anchors = self.__rects_to_anchors(named_rects.values())
        self.center_var = torch.tensor([0.,0.])
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
        fp.util.check.valid_rects(detected_rects)
        if para_init is not None:
            assert isinstance(para_init, list) or isinstance(para_init, tuple)
            
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
        if self.debug is not None:
            self.debug['warped_rects'] = warped_rects
            
        new_rects, succeed = self.associate(warped_rects, self.aligns, detected_rects)
        new_named_rects = {name : rect for name, rect in zip(self.names, new_rects)}
        print('new_rects:\n', new_rects)

        if update:
            # TODO: fix this
            new_center, new_anchors = self.__rects_to_anchors(new_rects, inline=False)
            self._update(new_center, new_anchors, para_final, succeed)
            
        
                
        return new_named_rects
                
    def _update(self, new_center, new_anchors, para_final, succeed):
        assert new_anchors is not None
        assert len(new_anchors) == len(self.anchors)
        
        # todo : update center
        _vector_update(self.center, self.center_var, new_center, self.count)
        
        for j in range(len(self.anchors)):
            if succeed[j] == 0:
                continue
            new_anchor = new_anchors[j]
            _vector_update(self.anchors[j], self.anchors_var[j], new_anchor, self.count)

        self.count += 1
        

    def __rects_to_anchors(self, rects, inline=True):
        # todo : copy cvt ?
        assert len(rects) == len(self.aligns)
        anchors = torch.stack([ReMap(align, self.std_size).to_anchor(rect, inline) \
                              for align, rect in zip(self.aligns, rects)])
        center = torch.mean(anchors[:, :2], dim=0)
        anchors[:, :2] -= center
        return center, anchors