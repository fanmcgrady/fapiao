import numpy as np

def intersect(rect0, rect1):
    xp, yp, wp, hp = rect0
    xq, yq, wq, hq = rect1
    x0 = max(xp, xq)
    y0 = max(yp, yq)
    x1 = min(xp + wp, xq + wq)
    y1 = min(yp + hp, yq + hq)
    return x0, y0, x1 - x0, y1 - y0


def iou(rect0, rect1):
    inter_rect = intersect(rect0, rect1)
    if inter_rect[2] <= 0 or inter_rect[3] <= 0:
        return 0
    inter = inter_rect[2] * inter_rect[3]
    area0 = rect0[2] * rect0[3]
    area1 = rect1[2] * rect1[3]
    union = area0 + area1 - inter
    return inter / union


def bounding_rect(rects):
    rects = np.array(rects)
    x0 = np.min(rects[:, 0])
    y0 = np.min(rects[:, 1])
    x1 = np.max(rects[:, 0] + rects[:, 2])
    y1 = np.max(rects[:, 1] + rects[:, 3])
    return x0, y0, x1 - x0, y1 - y0
