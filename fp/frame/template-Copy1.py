import os
import importlib
import numpy as np
import cv2
import torch
import torchvision

def alignment(name):
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

def warp_translate(detection, t):
    #return torch.stack([[x + t[0], y + t[1], w, h] for x, y, w, h in detection])
    dtc = detection.clone()
    dtc[:, :2] += t
    return dtc

def cost(template, detection):
    sd_cs = []
    for name, rect in template.items():
        align_code = alignment(name)
        tx, ty, tw, th = torch.tensor(rect).float()
        sd_c0 = []
        sd_c1 = []
        sd_c2 = []
        sd_c3 = []
        for dx, dy, dw, dh in detection:
            sd_x0 = (tx - dx)**2
            sd_x1 = (tx + tw - dx - dw)**2
            sd_y0 = (ty - dy)**2
            sd_y1 = (ty + th - dy - dh)**2
            sd_c0.append(sd_x0 + sd_y0)
            sd_c1.append(sd_x0 + sd_y1)
            sd_c2.append(sd_x1 + sd_y1)
            sd_c3.append(sd_x1 + sd_y0)
        sd_c0 = torch.stack(sd_c0)
        sd_c1 = torch.stack(sd_c1)
        sd_c2 = torch.stack(sd_c2)
        sd_c3 = torch.stack(sd_c3)
        sd_c0_min, _ = torch.min(sd_c0, dim=0)
        sd_c1_min, _ = torch.min(sd_c1, dim=0)
        sd_c2_min, _ = torch.min(sd_c2, dim=0)
        sd_c3_min, _ = torch.min(sd_c3, dim=0)
        if align_code == 3 or align_code == 0:
            v = (sd_c0_min + sd_c1_min + sd_c2_min + sd_c3_min) / 4
        elif align_code == 1:
            v = (sd_c0_min + sd_c1_min) / 2
        else:
            v = (sd_c2_min + sd_c3_min) / 2
        sd_cs.append(v)
    sd_cs = torch.stack(sd_cs)
    sd_cs_mean = torch.mean(sd_cs)
    return sd_cs_mean

class TemplateMatch(object):
    def __init__(self, template, warp_func, cost_func, learning_rate=0.1, epochs=100):
        self.template = {name : torch.tensor(rect).float() for name, rect in template.items()}
        self.warp = warp_func
        self.cost = cost_func
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.epsilon = 0.0001
        
    def __call__(self, detection, t_init=[0., 0.]):
        t = torch.tensor(t_init, requires_grad=True)
        detection = torch.tensor(detection).float()
        for i in range(self.epochs):
            warped_detec = self.warp(detection, t)
            loss = self.cost(self.template, warped_detec)
            loss.backward()
            if i % (self.epochs//10) == 0:
                t_str = ' '.join(['{:10.4f}'.format(ti) for ti in t])
                tg_str = ' '.join(['{:10.4f}'.format(ti) for ti in t.grad])
                print('{:4d}|{:10.4f}|{:24s}|{:24s}'.format(i, loss.item(), t_str, tg_str))
                
            if torch.norm(t.grad) < self.epsilon:
                print('early break')
                break

            with torch.no_grad():
                t -= self.learning_rate * t.grad
                # Manually zero the gradients after updating weights
                t.grad.zero_()
        
        return t, warped_detec.detach().cpu().numpy()
    
def evaluate(template, detection, im_shape):
    im_tpl = np.zeros(im_shape, np.uint8)
    im_dtc = np.zeros(im_shape, np.uint8)
    if torch.is_tensor(list(template.values())[0]):
        for x, y, w, h in template.values():
            x = int(round(x.item()))
            y = int(round(y.item()))
            w = int(round(w.item()))
            h = int(round(h.item()))
            im_tpl[y:y+h, x:x+w] = 255
    else:
        for x, y, w, h in template.values():
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
        