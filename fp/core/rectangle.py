import numpy as np


def intersect(rect0, rect1):
    xp, yp, wp, hp = rect0
    xq, yq, wq, hq = rect1
    x0 = max(xp, xq)
    y0 = max(yp, yq)
    x1 = min(xp + wp, xq + wq)
    y1 = min(yp + hp, yq + hq)
    return x0, y0, x1 - x0, y1 - y0
