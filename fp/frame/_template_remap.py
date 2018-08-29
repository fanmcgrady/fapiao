import importlib
import numpy as np
import torch
import torchvision

FIXED = 0
LEFT = 1
RIGHT = 2
CENTER = 3

def align_code(name):
    '''
    example:
         name    | return 
        ---------+--------
        'name'   | 0
        'name_'  | 1
        '_name'  | 2
        '_name_' | 3
    '''
    space_l = 2 if name[0] == '_' else 0
    space_r = 1 if name[-1] == '_' else 0
    return space_l + space_r

class ReMap(object):
    def __init__(self, align_code, std_size):
        assert isinstance(align_code, int)
        self.code = align_code
        self.std_size = std_size
        
    def to_anchor(self, rect, inline=True):
        '''
        used in match and update
        '''
        if isinstance(rect, tuple) or isinstance(rect, list):
            rect = torch.tensor(rect, dtype=torch.float32)
        if isinstance(rect, np.ndarray):
            rect = torch.from_numpy(rect).float()
        assert torch.is_tensor(rect)
        if inline:
            anchor = rect
        else:
            anchor = rect.clone()
        # rect to anchor
        if self.code == RIGHT:
            anchor[0] += anchor[2]
        elif self.code == CENTER or self.code == FIXED:
            anchor[0] += anchor[2]/2
        anchor[1] += anchor[3]/2
        # to relative coord
        for i in range(4):
            anchor[i] /= self.std_size[i % 2]

        return anchor
    
    def to_rect(self, anchor, inline=False):
        '''
        used in associate
        '''
        assert torch.is_tensor(anchor)
        if inline:
            rect = anchor
        else:
            rect = anchor.clone()
        # to absolute coord
        for i in range(4):
            rect[i] *= self.std_size[i % 2]
        # anchor to rect    
        if self.code == RIGHT:
            rect[0] -= rect[2]
        elif self.code == CENTER or self.code == FIXED:
            rect[0] -= rect[2]/2
        rect[1] -= rect[3]/2
        return rect