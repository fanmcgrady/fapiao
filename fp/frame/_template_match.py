import os
import importlib
import numpy as np
import cv2
import torch
import torchvision

import fp.config

class TemplateMatch(object):
    def __init__(self, cost, warp,
                 learning_rate=0.2, iteration=2000, num_try=20,
                 debug=False):
        self.warp = warp
        self.cost = cost
        self.learning_rate = learning_rate
        self.iteration = iteration
        self.num_try = num_try
        self.debug = dict() if debug else None
        if self.debug is not None:
            print('TemplateMatch is in debug mode')

    def __call__(self, anchors_mean, center_mean, aligns, 
                 detected_candidates, para_init=None):
        '''input should be tensors'''
        if self.debug is not None:
            self.debug['warp_history'] = []
        
        # use given init para or choose from random guess
        if para_init is not None:
            para = self.warp.init(para_init)
        else:
            loss = None
            para = None
            for try_count in range(self.num_try):
                _para = self.warp.init()
                _warped_anchors = self.warp(anchors_mean, center_mean, _para)
                _loss = self.cost(_warped_anchors, aligns, detected_candidates)
                _loss = _loss.detach().item()
                if loss is None or loss > _loss:
                    loss = _loss
                    para = _para

        para, warped_anchors, loss = self._one_try(anchors_mean, center_mean, aligns, 
                                                   detected_candidates, para)
        return para, warped_anchors

    def _one_try(self, anchors_mean, center_mean, align, detected_candidates, para):
        '''input should be tensors'''
        #t = torch.tensor(t_init, requires_grad=True)
        
        if self.debug is not None:
            print('{:>4s}|{:>10s}|{:^24s}|{:^24s}'.format('i', 'loss', 't', 't_grad'))
            
        for i in range(self.iteration):
            warped_anchors = self.warp(anchors_mean, center_mean, para)
            if self.debug is not None:
                self.debug['warp_history'].append(warped_anchors.detach())
            loss = self.cost(warped_anchors, align, detected_candidates)
            ## @TODO: add prior restriction
            if len(para) == 4:
                prior_sx = torch.norm(para[2] - 1.)
                prior_sy = torch.norm(para[3] - 1.)
                loss += 0.002 * prior_sx + 0.001 * prior_sy
            loss.backward()
            
            if self.debug is not None and i % (self.iteration//10) == 0:
                t_str = ' '.join(['{:10.4f}'.format(ti) for ti in para])
                tg_str = ' '.join(['{:10.4f}'.format(ti) for ti in para.grad])
                print('{:4d}|{:10.4f}|{:24s}|{:24s}'.format(i, loss.item(), t_str, tg_str))
                
            if torch.norm(para.grad) < fp.config.EPSILON:
                break
                if self.debug is not None:
                    print('early break')

            with torch.no_grad():
                para -= self.learning_rate * para.grad
                # Manually zero the gradients after updating weights
                para.grad.zero_()

        return para.detach().cpu(), warped_anchors.detach().cpu(), loss.detach().item()
    
    #def _anchor_candiates(self, warped_rects):
    #    x, y = warped_rects[:, 0], warped_rects[:, 1]
    #    w, h = warped_rects[:, 2], warped_rects[:, 3]
    #    xl, xc, xr = x, x + w / 2, x + w
    #    yc = y + h / 2
    #    
    #    detect_anchor_l = torch.stack((xl, yc, w, h), dim=1)
    #    detect_anchor_c = torch.stack((xc, yc, w, h), dim=1)
    #    detect_anchor_r = torch.stack((xr, yc, w, h), dim=1)
    #    
    #    return detect_anchor_l, detect_anchor_c, detect_anchor_r


def evaluate(anchors_mean, detection, im_shape):
    im_tpl = np.zeros(im_shape, np.uint8)
    im_dtc = np.zeros(im_shape, np.uint8)
    if torch.is_tensor(list(anchors_mean.values())[0]):
        for x, y, w, h in anchors_mean.values():
            x = int(round(x.item()))
            y = int(round(y.item()))
            w = int(round(w.item()))
            h = int(round(h.item()))
            im_tpl[y:y+h, x:x+w] = 255
    else:
        for x, y, w, h in anchors_mean.values():
            x = int(round(x))
            y = int(round(y))
            w = int(round(w))
            h = int(round(h))
            im_tpl[y:y+h, x:x+w] = 255
    for x, y, w, h in detection:
        x = int(round(x))
        y = int(round(y))
        w = int(round(w))
        h = int(round(h))
        im_dtc[y:y+h, x:x+w] = 255
    im_dif = cv2.absdiff(im_tpl, im_dtc)
    pix_inter = cv2.countNonZero(cv2.bitwise_and(im_tpl, im_dtc))
    pix_union = cv2.countNonZero(cv2.bitwise_or(im_tpl, im_dtc))
    return pix_inter / pix_union, im_dif
        