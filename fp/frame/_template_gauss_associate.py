import os
import importlib
import numpy as np
import torch
import torchvision

from . import _template_remap

importlib.reload(_template_remap)
from ._template_remap import ReMap, align_code, LEFT, CENTER, RIGHT


def _overlap_area(rect, rect_ref):
    x0, x1, y0, y1 = rect_to_limit(rect)
    u0, u1, v0, v1 = rect_to_limit(rect_ref)
    dxu = min(x1, u1) - max(x0, u0)
    dyv = min(y1, v1) - max(y0, v0)
    return dxu * dyv if dxu > 0 and dyv > 0 else 0


def rect_to_limit(rect):
    x, y, w, h = rect
    return x, x + w, y, y + h


def bounding_rect(rects):
    assert torch.is_tensor(rects) and rects.shape[1] == 4
    x0 = torch.min(rects[:, 0])
    y0 = torch.min(rects[:, 1])
    x1 = torch.max(rects[:, 0] + rects[:, 2])
    y1 = torch.max(rects[:, 1] + rects[:, 3])
    return torch.stack([x0, y0, x1 - x0, y1 - y0])


class RangeSaturate(object):
    def __init__(self, x_range, y_range):
        self.x0, self.x1 = x_range
        self.y0, self.y1 = y_range
        self.k = (self.y1 - self.y0) / (self.x1 - self.x0)

    def __call__(self, x):
        if x <= self.x0:
            return self.y0
        elif x >= self.x1:
            return self.y1
        else:
            return (x - self.x0) * self.k + self.y0


class TemplateAssociate_v2(object):
    def __init__(self, debug=False):
        self.inter_ratio = 0.4
        self.weights = torch.tensor([0.25, 0.25, 0.25, 0.25])
        self.debug = dict() if debug else None

    def __call__(self, warped_anchors, anchors_std, warped_rects,
                 aligns, detected_candidates, detected_rects, image_size, keys=None):
        assert len(warped_anchors) == len(aligns)
        n_anchors = len(aligns)
        n_detects = len(detected_rects)

        warped_rects_area = warped_rects[:, 2] * warped_rects[:, 3]
        detected_rects_area = detected_rects[:, 2] * detected_rects[:, 3]

        new_anchors = warped_anchors.clone()
        succeed = torch.zeros((n_anchors,), dtype=torch.uint8)
        # for each template rectangles
        for i in range(n_anchors):
            align = aligns[i]
            warped_anchor = warped_anchors[i]
            anchor_std = anchors_std[i]
            warped_rect = warped_rects[i]
            if align == LEFT:
                candidate_idx = 0
            elif align == RIGHT:
                candidate_idx = 2
            else:
                candidate_idx = 1
            detected_anchors = detected_candidates[candidate_idx]
            element_diffs = torch.abs(detected_anchors - warped_anchor) / anchor_std
            overall_diffs = torch.matmul(element_diffs, self.weights)
            # print('element_dif', element_diff)
            diff_min, diff_min_idx = torch.min(overall_diffs, dim=0)

            if self.debug is not None:
                print('key_id:{:2d} '.format(i))
                if keys is not None:
                    print('  {:10s} '.format(keys[i]))
                print('  diff_min:{:.4f} '.format(diff_min))

            # broken into pieces
            assoc_rects = []
            for j in range(n_detects):
                # if the detected is inside the template item
                detected_rect = detected_rects[j]
                inter_area = _overlap_area(detected_rect, warped_rect)
                inside_ratio = inter_area / detected_rects_area[j]
                outside_ratio = (detected_rects_area[j] - inter_area) / warped_rects_area[i]
                # print('    {:.4f}~{:.4f}'.format(inside_ratio, outside_ratio))
                if inside_ratio > self.inter_ratio and outside_ratio < 0.2:
                    assoc_rects.append(detected_rect)

            if len(assoc_rects) > 0:
                # print('#assoc {}'.format(assoc_rects), end='')
                new_rect = bounding_rect(torch.stack(assoc_rects))
                new_anchor = ReMap(align, image_size).to_anchor(new_rect)
                element_diff = torch.abs(new_anchor - warped_anchor) / anchor_std
                # print('new_anchor {}'.format(new_anchor))
                # print('warped_anchor {}'.format(warped_anchor))
                # print('anchor_std {}'.format(anchor_std))
                # print('element_diff {}'.format(element_diff), end='')
                overall_diff = torch.dot(element_diff, self.weights)
                if self.debug is not None:
                    print('  assoc rects')
                    for _i, _rect in enumerate(assoc_rects):
                        print('    {}: {}'.format(_i, _rect))
                    print('  assoc new_rect', new_rect)
                    print('  bndbox_diff {}'.format(overall_diff))
                if overall_diff < diff_min:
                    if overall_diff < 1.0:
                        new_anchors[i] = new_anchor
                        succeed[i] = 1
                        continue
                else:
                    if diff_min < 1.0:
                        new_anchors[i, :] = detected_anchors[diff_min_idx]
                        succeed[i] = 1
                        continue

            # the detected is a little bit larger
            _area = _overlap_area(warped_rect, detected_rects[diff_min_idx])
            rev_inside_ratio = _area / warped_rects_area[i]
            if self.debug is not None:
                print('  inside_ratio:{:.4f}'.format(rev_inside_ratio))
            if rev_inside_ratio > self.inter_ratio:
                detected_height = detected_rects[diff_min_idx][3]
                warped_height = warped_rect[3]
                if abs(detected_height - warped_height) / warped_height < 0.3:
                    new_anchors[i, :] = detected_anchors[diff_min_idx]
                    succeed[i] = 1
                    continue

            if self.debug is not None:
                print('  Not succeed')

        return new_anchors, succeed
