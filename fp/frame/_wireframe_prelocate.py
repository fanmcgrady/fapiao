import os
import sys
import importlib
import numpy as np
import cv2

from ..core import line


def evaluate_point_set(points, dist_th_ratio=0.05):
    box = cv2.minAreaRect(points)
    dist_th = np.min(box[1]) * dist_th_ratio
    # print(box, dist_th)
    box_points = cv2.boxPoints(box)
    border_points_idx = [[], [], [], []]
    for i, (x0, x1) in enumerate(zip(box_points, np.roll(box_points, 2))):
        # print(x0, x1)
        for j, p in enumerate(points):
            d = line.point_lineseg_distance(x0, x1, p)
            if d < dist_th:
                border_points_idx[i].append(j)

    return box, box_points, border_points_idx


class PreLocateWireframe(object):
    def __init__(self, debug=False):
        self.dist_th_ratio = 0.05
        self.debug = dict() if debug else None

    def __call__(self, points, image_size):
        '''Input a set of points, output points that may belong to a wireframe
        '''
        if len(points) < 3:
            return None, None
        box, box_points, border_points_idx = evaluate_point_set(points, self.dist_th_ratio)
        # print(border_points_idx)
        del_points_idx = []
        for i in range(4):
            border_i_points_idx = border_points_idx[i]
            if len(border_i_points_idx) == 1:
                del_point_idx = border_i_points_idx[0]
                if del_point_idx not in del_points_idx:
                    del_points_idx.append(del_point_idx)

        if len(del_points_idx) > 0:
            points = np.delete(points, del_points_idx, axis=0)
            box, box_points, border_points_idx = evaluate_point_set(points, self.dist_th_ratio)
            # print(border_points_idx)

        if self.debug is not None:
            self.debug['result'] = self._draw(image_size, points, box_points, border_points_idx)
        rectr = self.relative_rect(box_points, image_size)

        return box, rectr

    def relative_rect(self, box_points, image_size):
        w, h = image_size
        xs = np.array([p[0] for p in box_points])
        ys = np.array([p[1] for p in box_points])
        x0, x1 = np.min(xs), np.max(xs)
        y0, y1 = np.min(ys), np.max(ys)
        return x0 / w, y0 / h, (x1 - x0) / w, (y1 - y0) / h

    def _draw(self, image_size, points, box_points, border_points_idx):
        colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255))
        image = np.zeros((image_size[1], image_size[0], 3), dtype=np.uint8)
        for p in points:
            cv2.circle(image, tuple(p), 19, (255, 0, 0), 2)
        for i, (p0, p1) in enumerate(zip(box_points, np.roll(box_points, 2))):
            cv2.line(image, tuple(p0), tuple(p1), colors[i], 3)
            for pidx in border_points_idx[i]:
                p = points[pidx]
                cv2.circle(image, tuple(p), 9, colors[i], -1)
        return image
