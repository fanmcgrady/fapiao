import importlib
import numpy as np
import torch
import torchvision

class Warp(object):
    def __init__(self, method='translate'):
        '''
        Arg:
          method : (str) 'translate' or 'trans_scale'
        '''
        if method == 'translate':
            # self._para_init = [0., 0.]
            rx = np.random.randint(-7, 8)
            ry = np.random.randint(-17, 18)
            self._para_init = [1. * rx, 1. * ry]
        else:
            self._para_init = [0., 0., 1., 1.]

    def init(self, para_init=None):
        if para_init is None or len(para_init) != len(self._para_init):
            rx = np.random.randint(-27, 28) / 683.
            ry = np.random.randint(-47, 48) / 435.
            self._para_init = [1. * rx, 1. * ry]
            para_init = self._para_init
        return torch.tensor(para_init, requires_grad=True)

    def __call__(self, anchors, center, para):
        '''
        Arg:
          para : (tensor with grad) (tx, ty) or (tx, ty, sx, sy)
        '''
        assert len(para) == 2 or len(para) == 4
        assert torch.is_tensor(para)

        x, y = anchors[:, 0], anchors[:, 1]
        w, h = anchors[:, 2], anchors[:, 3]
        if len(para) == 4:
            X = para[2] * x + para[0] + center[0]
            Y = para[3] * y + para[1] + center[1]
        else:
            X = x + para[0] + center[0]
            Y = y + para[1] + center[1]
        # W = w * para[2] if len(para) == 4 else w
        #H = h * para[3] if len(para) == 4 else h
        
        warped_abs_anchors = torch.stack((X, Y, w, h), dim=1)
        return warped_abs_anchors