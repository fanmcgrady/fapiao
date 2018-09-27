import os
import numpy as np
import torch
import torchvision

from .. import config


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
    def __init__(self, y_ratios, x_ratiox):
        px = relative_points(y_ratios, x_ratiox)
        ps = []
        for p in px:
            ps.extend(p)
        self.points = torch.tensor(ps)
        self.points_std = torch.ones((len(ps),), dtype=torch.float32)
        # self.points = None
        # self.points_std = None

    def fit(self, xml_files):
        pass

    def rand_init(self):
        return None


def min_dist_loss(self, ps, detection):
    glotbal_dists = []
    for p in ps:
        dists = torch.norm(detection - p, dim=1)
        dist_min, _ = torch.min(dists, dim=0)
        global_dists.append(dist_min)
    global_dists = torch.stack(global_dists)
    return torch.mean(global_diss)


class WireframeTemplate(object):
    def __init__(self, data, loss):
        ''''''
        self.data = data
        self.loss = loss

        self.learning_rate = 0.1
        self.max_iteration = 3000
        self.num_try = 20

    def _warp(self, rectr):
        xr, yr, wr, hr = rectr
        ps = self.points
        ps = torch.stack([ps[:, 0] * wr + xr, ps[:, 1] * hr + yr], dim=1)
        return ps

    def __call__(self, detection, std_size):
        dr = torch.from_numpy(detection) / torch.tensor(std_size)

        loss_val = None
        for try_count in range(self.num_try):
            _rectr = self.data.rand_init()
            warped_points = self._warp(_rectr)
            _loss = self.cost(warped_points, dr)
            _loss = _loss.detach().item()
            if loss_val is None or loss_val > _loss:
                loss_val = _loss
                rectr = _rectr

        for i in range(self.max_iteration):
            warped_points = self._warp(rectr)
            loss = self.loss(warped_points, dr)
            if False:
                prior_sx = torch.norm(rectr[2] - 1.)
                loss += prior_sx
            loss.backward()

            if torch.norm(para.grad) < config.EPSILON:
                break

            with torch.no_grad():
                rectr -= self.learning_rate * rectr.grad
                # Manually zero the gradients after updating weights
                rectr.grad.zero_()

        return para.detach().cpu(), warped_anchors.detach().cpu(), loss.detach().item()
