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

from . import _template_gauss_associate

importlib.reload(_template_gauss_associate)
from ._template_gauss_associate import TemplateAssociate_v2

from . import _template_cost
importlib.reload(_template_cost)
from ._template_cost import TemplateCost

from . import _template_warp
importlib.reload(_template_warp)
from ._template_warp import Warp

from . import _template_remap
importlib.reload(_template_remap)
from ._template_remap import ReMap, align_code

from ..model import pascal_voc

importlib.reload(pascal_voc)

from . import template_data

importlib.reload(template_data)
from .template_data import TemplateData

from ..util import check

importlib.reload(check)

def named_rects_from_xml(xmlfile):
    '''use pascal voc as named rects'''
    objects = pascal_voc.parse_xml(xmlfile)['objects']
    return {item['name'] : item['bndbox'] for item in objects}


def anchors_candidates(rects, image_size):
    x, y = rects[:, 0], rects[:, 1]
    w, h = rects[:, 2], rects[:, 3]
    xl = (x) / image_size[0]
    xc = (x + w / 2) / image_size[0]
    xr = (x + w) / image_size[0]
    yc = (y + h / 2) / image_size[1]
    w_ = w / image_size[0]
    h_ = h / image_size[1]
    anchors_l = torch.stack((xl, yc, w_, h_), dim=1)
    anchors_c = torch.stack((xc, yc, w_, h_), dim=1)
    anchors_r = torch.stack((xr, yc, w_, h_), dim=1)
    return anchors_l, anchors_c, anchors_r
    
class Template(object):
    '''
    template is represented by anchors
    '''

    def __init__(self, init_yaml=None,
                 warp_method='translate',
                 learning_rate=0.01, max_iters=3000, debug=False):
        '''
        '''
        self.data = TemplateData()
        if init_yaml is not None and isinstance(init_yaml, str):
            self.data.load(init_yaml)
        
        self.warp = Warp(warp_method)
        self.cost = TemplateCost()
        self.match = TemplateMatch(cost=self.cost, warp=self.warp,
                                   learning_rate=learning_rate, iteration=max_iters,
                                   debug=debug)
        # self.associate = TemplateAssociate()
        self.associate2 = TemplateAssociate_v2(debug=debug)

        self.debug = dict() if debug else None
        if self.debug is not None:
            print('Template in debug mode')

    def __call__(self, detected_rects, image_size, para_init=None, update=False):
        assert check.valid_rects(detected_rects)
        assert check.valid_size(image_size)
        assert self.data.keys is not None
        if para_init is not None:
            assert isinstance(para_init, list) or isinstance(para_init, tuple)

        assert self.data.keys is not None
        aligns = list(map(align_code, self.data.keys))
        detected_rects = torch.tensor(detected_rects).float()
        detected_candidates = anchors_candidates(detected_rects, image_size)

        para_final, warped_anchors = self.match(self.data.anchors_mean,
                                                self.data.center_mean,
                                                aligns,
                                                detected_candidates,
                                                para_init)
        
        if self.debug is not None:
            warped_rects_history = []
            for warped_anchors_i in self.match.debug['warp_history']:
                warped_rects_i = torch.stack([ReMap(align, image_size).to_rect(anchor) \
                                              for align, anchor in zip(aligns, warped_anchors_i)])
                warped_rects_history.append(warped_rects_i)
            self.debug['warped_rects_history'] = warped_rects_history

        warped_rects = torch.stack([ReMap(align, image_size).to_rect(anchor) \
                                    for align, anchor in zip(aligns, warped_anchors)])
        if self.debug is not None:
            self.debug['warped_rects'] = warped_rects

        new_anchors, succeed = self.associate2(warped_anchors,
                                               self.data.anchors_std,
                                               warped_rects,
                                               aligns,
                                               detected_candidates,
                                               detected_rects,
                                               image_size,
                                               self.data.keys)
        new_named_rects = {key: ReMap(align, image_size).to_rect(anchor) \
                           for key, align, anchor in zip(self.data.keys, aligns, new_anchors)}
        if update:
            # TODO: fix this
            self.data.update(new_anchors, succeed)

        return new_named_rects, succeed
