import os
import importlib
import numpy as np
import cv2
import torch
import torchvision

import fp.config

class TemplateMatch(object):
    def __init__(self, cost, warp, learning_rate=0.01, iteration=1000):
        self.warp = warp
        self.cost = cost
        self.learning_rate = learning_rate
        self.iteration = iteration
        
    def __call__(self, anchors, center, align, detected_rects, para_init=None, to_show=True):
        '''input should be tensors'''
        self.warped_abs_anchors_history = []
        if para_init is not None:
            para, warped_abs_anchors, loss = self.one_try(anchors, center, align, 
                                                          detected_rects, para_init, to_show)
            return para, warped_abs_anchors
        else:
            best_loss = None
            best_para = None
            best_warped_abs_anchors = None
            for try_count in range(4):
                para, warped_abs_anchors, loss = self._one_try(anchors, center, align, 
                                                               detected_rects, None, to_show)
                if best_loss is None or best_loss > loss:
                    best_para = para
                    best_warped_abs_anchors = warped_abs_anchors
            return best_para, best_warped_abs_anchors
        
    def _one_try(self, anchors, center, align, detected_rects, para_init=None, to_show=True):
        '''input should be tensors'''
        #t = torch.tensor(t_init, requires_grad=True)
        para = self.warp.init(para_init)
        if to_show:
            print('{:>4s}|{:>10s}|{:^24s}|{:^24s}'.format('i', 'loss', 't', 't_grad'))
            
        for i in range(self.iteration):
            warped_abs_anchors = self.warp(anchors, center, para)
            self.warped_abs_anchors_history.append(warped_abs_anchors)
            loss = self.cost(warped_abs_anchors, align, detected_rects)
            ## @TODO: add prior restriction
            if len(para) == 4:
                prior_sx = torch.norm(para[2] - 1.)
                prior_sy = torch.norm(para[3] - 1.)
                loss += 0.002 * prior_sx + 0.001 * prior_sy
            loss.backward()
            
            if to_show and i % (self.iteration//10) == 0:
                t_str = ' '.join(['{:10.4f}'.format(ti) for ti in para])
                tg_str = ' '.join(['{:10.4f}'.format(ti) for ti in para.grad])
                print('{:4d}|{:10.4f}|{:24s}|{:24s}'.format(i, loss.item(), t_str, tg_str))
                
            if to_show and torch.norm(para.grad) < fp.config.EPSILON:
                print('early break')
                break

            with torch.no_grad():
                para -= self.learning_rate * para.grad
                # Manually zero the gradients after updating weights
                para.grad.zero_()
        
        return para, warped_abs_anchors.detach().cpu(), loss.detach().item()
    
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
    
def evaluate(anchors, detection, im_shape):
    im_tpl = np.zeros(im_shape, np.uint8)
    im_dtc = np.zeros(im_shape, np.uint8)
    if torch.is_tensor(list(anchors.values())[0]):
        for x, y, w, h in anchors.values():
            x = int(round(x.item()))
            y = int(round(y.item()))
            w = int(round(w.item()))
            h = int(round(h.item()))
            im_tpl[y:y+h, x:x+w] = 255
    else:
        for x, y, w, h in anchors.values():
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
        