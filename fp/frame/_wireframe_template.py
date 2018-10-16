import os
import importlib
import numpy as np
import torch
import torchvision
import yaml

from .. import config
importlib.reload(config)
from . import template_data
importlib.reload(template_data)

def relative_points(y_ratios, x_ratiox):
    ps = []
    y_ratios = [0., *y_ratios, 1.]
    n = len(y_ratios) - 1
    assert len(x_ratiox) == n

    for j, yr in enumerate(y_ratios):
        psj = [(0., yr)]
        if j < n:
            for xr in x_ratiox[j]:
                psj.append((xr, yr))
        if j > 0:
            for xr in x_ratiox[j - 1]:
                psj.append((xr, yr))
        psj.append((1., yr))
        ps.append(sorted(psj, key=lambda x: x[0]))
    return ps

class WireframeTemplateData(object):
    def __init__(self, y_ratios=None, x_ratiox=None):
        if y_ratios == None or x_ratiox == None:
            return

        # self.points = None
        # self.points_std = None
    
    def fit(self, xml_files, prior):
        '''
        Args:
          prior dict(frame_key=[], rectx_key=[[]] )
        '''
        batch_rectr = []
        batch_y_ratios = []
        batch_x_ratiox = []
        for xml_file in xml_files:
            named_rects, image_size = template_data.xml_info(xml_file)
            frame_key = prior['frame_key']
            rectx_key = prior['rectx_key']

            rectx_rows = len(rectx_key)
            xa, ya, wa, ha = named_rects[frame_key]
            rectr = (xa / image_size[0], ya / image_size[1], \
                     wa / image_size[0], ha / image_size[1])
            batch_rectr.append(rectr)

            y_ratios = []
            x_ratiox = []
            for j, rects_key in enumerate(rectx_key):
                x_ratios = []
                for i, rect_key in enumerate(rects_key):
                    xji, yji, wji, hji = named_rects[rect_key]

                    # make y_ratios
                    if i == 0 and j < rectx_rows - 1:
                        y_ratios.append((yji + hji - ya) / ha)

                    # make x_ratiox
                    x_ratios.append((xji - xa) / wa)
                    if i < len(rects_key) - 1:
                        x_ratios.append((xji + wji - xa) / wa) 
                    else:
                        if abs(xji + wji - xa - wa) > 10:
                            x_ratios.append((xji + wji - xa) / wa)

                    #print(j, i, rect_key, len(y_ratios))
                x_ratiox.append(x_ratios)

            # print(len(y_ratios))
            # print(len(x_ratiox))
            #for x_ratios in x_ratiox:
            #    print('  ', len(x_ratios))
            batch_y_ratios.append(y_ratios)
            batch_x_ratiox.append(x_ratiox)

        batch_rectr = torch.tensor(batch_rectr)
        #print(batch_rectr.shape)
        rectr = torch.mean(batch_rectr, dim=0)
        rectr_std = torch.std(batch_rectr, dim=0)
        self.rectr = rectr
        self.rectr_std = rectr_std

        batch_y_ratios = torch.tensor(batch_y_ratios)
        #print(batch_y_ratios.shape)
        y_ratios = torch.mean(batch_y_ratios, dim=0)
        y_ratios_std = torch.std(batch_y_ratios, dim=0)
        self.y_ratios = y_ratios
        self.y_ratios_std = y_ratios_std

        x_ratiox = []
        x_ratiox_std = []
        for i in range(len(batch_x_ratiox[0])):
            # store all i-th row
            batch_x_ratios = []
            for c in range(len(batch_x_ratiox)):
                batch_x_ratios.append(batch_x_ratiox[c][i])
            batch_x_ratios = torch.tensor(batch_x_ratios)
            x_ratios = torch.mean(batch_x_ratios, dim=0)
            x_ratios_std = torch.std(batch_x_ratios, dim=0)
            x_ratiox.append(x_ratios)
            x_ratiox_std.append(x_ratios_std)
            #print(x_ratios.shape, x_ratios_std.shape)
        
        self.x_ratiox = x_ratiox
        self.x_ratiox_std = x_ratiox_std

    def rand_rectr(self):
        return torch.normal(self.rectr, self.rectr_std)

    def load(self, filename):
        assert isinstance(filename, str)
        if filename[-5:].lower() != '.yaml':
            filename = filename + '.yaml'
        assert os.path.isfile(filename)

        with open(filename, 'r') as fp:
            dict_load = yaml.load(fp.read())
            fp.close()

        self.rectr = torch.tensor(dict_load['rectr'])
        self.rectr_std = torch.tensor(dict_load['rectr_std'])
        self.y_ratios = torch.tensor(dict_load['y_ratios'])
        self.y_ratios_std = torch.tensor(dict_load['y_ratios_std'])
        x_ratiox = dict_load['x_ratiox']
        self.x_ratiox = [torch.tensor(x_ratios) for x_ratios in x_ratiox]
        x_ratiox_std = dict_load['x_ratiox_std']
        self.x_ratiox_std = [torch.tensor(x_ratios_std) for x_ratios_std in x_ratiox_std]

    def save(self, filename):
        assert isinstance(filename, str)
        if filename[-5:].lower() != '.yaml':
            filename = filename + '.yaml'

        with open(filename, 'w') as fp:
            x_ratiox = [template_data.tensor_to_list(x_ratios) for x_ratios in self.x_ratiox]
            x_ratiox_std = [template_data.tensor_to_list(x_ratios_std) for x_ratios_std in self.x_ratiox_std]
            dict_save = dict(rectr=template_data.tensor_to_list(self.rectr),
                             rectr_std=template_data.tensor_to_list(self.rectr_std),
                             y_ratios=template_data.tensor_to_list(self.y_ratios),
                             y_ratios_std=template_data.tensor_to_list(self.y_ratios_std),
                             x_ratiox=x_ratiox,
                             x_ratiox_std=x_ratiox_std)
            fp.write(yaml.dump(dict_save))
            fp.close()


def min_dist_loss(template_points, detected_points):
    global_dists = []
    for p in template_points:
        dists = torch.norm(detected_points - p, dim=1)
        dist_min, _ = torch.min(dists, dim=0)
        global_dists.append(dist_min)
    global_dists = torch.stack(global_dists)
    return torch.mean(global_dists)

class WireframeTemplate(object):
    def __init__(self, data, loss=min_dist_loss, debug=False):
        ''''''
        self.data = data
        px = relative_points(data.y_ratios, data.x_ratiox)
        ps = []
        for p in px:
            ps.extend(p)
        self.points = torch.tensor(ps)
        self.points_std = torch.ones((len(ps),), dtype=torch.float32)
        self.loss = loss

        self.learning_rate = 0.001
        self.max_iteration = 3000
        self.num_try = 20

        self.rectr = None

        self.debug = dict() if debug else None
        
    def _warp(self, rectr):
        xr, yr, wr, hr = rectr
        ps = self.points
        ps = torch.stack([ps[:, 0] * wr + xr, ps[:, 1] * hr + yr], dim=1)
        return ps

    def __call__(self, detected_points, image_size):
        ''''''
        self.rectr = None
        image_size = torch.tensor(image_size, dtype=torch.float32)
        rel_detected_points = torch.from_numpy(detected_points) / image_size

        loss_val = None
        for try_count in range(self.num_try):
            _rectr = self.data.rand_rectr()
            warped_points = self._warp(_rectr)
            _loss = self.loss(warped_points, rel_detected_points)
            _loss = _loss.detach().item()
            if loss_val is None or loss_val > _loss:
                loss_val = _loss
                rectr = _rectr

        rectr.requires_grad = True
        for i in range(self.max_iteration):
            warped_points = self._warp(rectr)
            loss = self.loss(warped_points, rel_detected_points)
            if False:
                prior_sx = torch.norm(rectr[2] - 1.)
                loss += prior_sx
            loss.backward()

            if self.debug is not None and i % (self.max_iteration // 10) == 0:
                t_str = ' '.join(['{:10.4f}'.format(t) for t in rectr])
                g_str = ' '.join(['{:10.4f}'.format(t) for t in rectr.grad])
                print('{:4d}|{:10.4f}|{:24s}|{:24s}'.format(i, loss.item(), t_str, g_str))

            if torch.norm(rectr.grad) < config.EPSILON:
                break

            with torch.no_grad():
                rectr -= self.learning_rate * rectr.grad
                # Manually zero the gradients after updating weights
                rectr.grad.zero_()

        self.rectr = rectr        
        # slice rects
        return rectr.detach().cpu()

    def roi(self, image_size, row, col):
        assert self.rectr is not None
        W, H = image_size
        x, y, w, h = self.rectr * torch.tensor([W, H, W, H], dtype=torch.float32)

        if row == -1:
            y0 = 0
            y1 = int(round(y.item()))
            if col == 0:
                x0 = 0
                x1 = int(round((x + w * 0.33).item()))
            elif col == 1:
                x0 = int(round((x + w * 0.33).item()))
                x1 = int(round((x + w * 0.67).item()))
            else:
                x0 = int(round((x + w * 0.67).item()))
                x1 = W
            return x0, y0, x1 - x0, y1-y0
        
        y_ratios = self.data.y_ratios
        if row == 0:
            yr0 = 0.0
            yr1 = y_ratios[row]
        elif row == len(y_ratios):
            yr0 = y_ratios[row - 1]
            yr1 = 1.0
        else:
            yr0 = y_ratios[row - 1]
            yr1 = y_ratios[row]

        x_ratios = self.data.x_ratiox[row]
        if col == 0:
            xr0 = 0.0
            xr1 = x_ratios[col]
        elif col == len(x_ratios):
            xr0 = x_ratios[col - 1]
            xr1 = 1.0
        else:
            xr0 = x_ratios[col - 1]
            xr1 = x_ratios[col]

        x0 = int(round((x + w * xr0).item()))
        x1 = int(round((x + w * xr1).item()))
        y0 = int(round((y + h * yr0).item()))
        y1 = int(round((y + h * yr1).item()))

        return x0, y0, x1 - x0, y1-y0
