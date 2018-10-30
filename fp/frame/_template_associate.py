import os
import importlib
import numpy as np
import torch
import torchvision


# from . import _template_remap
# importlib.reload(_template_remap)
# from ._template_remap import ReMap

def rect_to_limit(rect):
    x, y, w, h = rect
    return x, x + w, y, y + h

def rect_overlap_area(rect, rect_ref):
    x0, x1, y0, y1 = rect_to_limit(rect)
    u0, u1, v0, v1 = rect_to_limit(rect_ref)
    dxu = min(x1, u1) - max(x0, u0)
    dyv = min(y1, v1) - max(y0, v0)
    if dxu > 0 and dyv > 0:
        return dxu * dyv
    else:
        return 0


def bounding_rect(rects):
    if rects == []:
        return None
    limits = list(map(rect_to_limit, rects))
    x0 = np.min([x0 for x0, x1, y0, y1 in limits])
    x1 = np.max([x1 for x0, x1, y0, y1 in limits])
    y0 = np.min([y0 for x0, x1, y0, y1 in limits])
    y1 = np.min([y1 for x0, x1, y0, y1 in limits])
    return np.array([x0, y0, x1 - x0, y1 - y0], np.float32)

def approx(x0, x1):
    '''0 is best'''
    return abs(x0 - x1) / (x0 + x1)

def anchor_to_rect(anchor, align_code):
    rect = anchor.clone()
    rect[1] -= rect[3]/2
    if align_code == 2:
        rect[0] -= rect[2]
    elif align_code == 0 or align_code == 3:
        rect[0] -= rect[2]/2
    return rect


class TemplateAssociate(object):
    def __init__(self, iou_th=0.5, height_th=0.2, tiny_th=0.85):
        self.iou_th = iou_th
        self.height_th = height_th
        self.tiny_th = tiny_th

    def __call__(self, warped_rects, aligns, detected_rects):
        return self._simple_associate(warped_rects, aligns, detected_rects)

    def _simple_associate(self, warped_rects, aligns, detected_rects):
        '''
        Args:
            warped_rects   : warped template
            aligns         : alignment of each template rects
            detected_rects : detected rects, maybe clutted or missing
        '''
        new_rects = warped_rects.clone()
        succeed = torch.zeros((len(warped_rects),), dtype=torch.uint8)
        for i, (align_code, warped_rect) in enumerate(zip(aligns, warped_rects)):
            warped_rect_area = warped_rect[2] * warped_rect[3]
            assoc_detected_rects = []
            for detected_rect in detected_rects:
                overlap_area = rect_overlap_area(warped_rect, detected_rect)
                if overlap_area == 0:
                    continue
                detected_rect_area = detected_rect[2] * detected_rect[3]
                union_area = detected_rect_area + detected_rect_area - overlap_area
                iou = overlap_area / union_area

                # found
                if iou > self.iou_th:
                    assoc_detected_rects.append(detected_rect)
                    break

                # found
                if iou > 0.5 * self.iou_th and approx(warped_rect[3], detected_rect[3]) < self.height_th:
                    assoc_detected_rects.append(detected_rect)
                    break

                # if detection is cluttered, detected rect are small
                # found a piece
                if overlap_area / detected_rect_area > self.tiny_th:
                    assoc_detected_rects.append(detected_rect)

            bound_rect = bounding_rect(assoc_detected_rects)
            # compare the bound_rect to template, 
            if bound_rect is not None:
                new_rects[i, :] = torch.from_numpy(bound_rect)
                succeed[i] = 1
        return new_rects, succeed

    def _good_detect(self, warped_rect, new_rect):
        '''
        '''
        return True
