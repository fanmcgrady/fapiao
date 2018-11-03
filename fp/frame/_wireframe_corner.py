import importlib
import numpy as np
import cv2
import sklearn
import sklearn.cluster
import matplotlib.pyplot as pl

# import fp.util.io
# importlib.reload(fp.util.io)
from ..core import line as lineseg

importlib.reload(lineseg)

from ..util import check

importlib.reload(check)


class LineSegDetect(object):
    def __init__(self, debug=False):
        # opencv lSD seems to have a bug: 
        # it report Segment Fault from time to time
        self.debug = dict() if debug else None

    def __call__(self, image):
        '''input gray image'''
        # detect lines
        lsd = cv2.createLineSegmentDetector()
        lines, width, prec, nfa = lsd.detect(image)
        lines = np.squeeze(lines)

        # keep long lines
        _line_lens = list(map(lineseg.line_length, lines))
        _line_len_th = 0.75 * np.mean(_line_lens)
        keep_long_line = lambda x: lineseg.line_length(x) > _line_len_th
        linex = filter(keep_long_line, lines)
        linex = np.array(list(linex))

        if self.debug is not None:
            _disp = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            for x0, y0, x1, y1 in linex:
                cv2.line(_disp, (x0, y0), (x1, y1), (255, 0, 0), 2)
            self.debug['result'] = _disp
            # pl.figure()
            # pl.imshow(self.debug['result'])
        return linex


class CornerPointDetect(object):
    def __init__(self):
        pass

    def __call__(self, lines):
        # calc corner points
        points = []
        lineid_pairs = []
        # print('CornerPointDetect::points start...', len(lines))
        for j in range(len(lines) - 1):
            assert check.valid_line(lines[j])
            for i in range(j + 1, len(lines)):
                assert check.valid_line(lines[i])
                ap = abs(lineseg.cos_intersect_angle(lines[j], lines[i]))
                # print(j, i, ap, end='')
                if ap < 0.02:
                    cp = lineseg.intersect_point(lines[j], lines[i])
                    dj = lineseg.intersect_point_dist(lines[j], cp)
                    di = lineseg.intersect_point_dist(lines[i], cp)
                    # print(cp, dj, di, end='')
                    if dj < 12 and di < 12:  # TODO:
                        # intersection point is close to each line
                        # print('True', end='')
                        points.append(cp)
                        lineid_pairs.append([j, i])
                # print('')
        points = np.array(points)
        lineid_pairs = np.array(lineid_pairs)
        # print('CornerPointDetect::points done, cluster start...')
        # DBSCAN cluster
        core_samples, labels = sklearn.cluster.dbscan(points, eps=6., min_samples=1)
        num_clusters = np.max(labels) + 1
        # print('CornerPointDetect::cluster done')
        clustered_points = []
        clustered_lineids = []
        for i in range(num_clusters):
            cluster_i_index = np.nonzero(labels == i)[0]
            cluster_i_center = np.median(points[cluster_i_index], axis=0)
            clustered_points.append(cluster_i_center)
            clustered_lineids.append(lineid_pairs[cluster_i_index].flatten())
        return np.array(clustered_points, dtype=np.float32), clustered_lineids


def find_rects(points):
    points = np.array(points)
    # assert isinstance(points, np.ndarray)
    ys = [p[1] for p in points]
    ys = np.array(ys).reshape(-1, 1)
    _, labels = sklearn.cluster.dbscan(ys, eps=6., min_samples=1)
    num_rows = np.max(labels) + 1
    _points = []
    for y in range(num_rows):
        idx = np.nonzero(labels == y)[0]
        _points.append(points[idx])
    _points.sort(key=lambda p: p[0][1])
    for i in range(len(_points)):
        _points[i] = sorted(list(_points[i]), key=lambda p: p[0])

    bars = []
    for y in range(num_rows - 1):
        row_bars = []
        points0 = _points[y]
        points1 = _points[y + 1]
        for x0, y0 in points0:
            for x1, y1 in points1:
                if abs(x0 - x1) < 4.0:
                    row_bars.append((x0, y0, x1, y1))
        bars.append(row_bars)

    l_bar = np.median([(bars[i][0][0] + bars[i][0][2]) / 2 for i in range(len(bars))])
    r_bar = np.median([(bars[i][-1][0] + bars[i][-1][2]) / 2 for i in range(len(bars))])

    rect_frame = []
    for y in range(num_rows - 1):
        # if abs((bars[y][0][0] + bars[y][0][2]) /2 - l_bar) > 8:
        #    bars[y].insert((
        rects = []
        for i in range(len(bars[y]) - 1):
            x0, y0, x1, y1 = bars[y][i]
            x2, y2, x3, y3 = bars[y][i + 1]
            x00 = (x0 + x1) / 2
            y00 = (y0 + y2) / 2
            x33 = (x2 + x3) / 2
            y33 = (y3 + y1) / 2
            rects.append((x00, y00, x33 - x00, y33 - y00))
        rect_frame.append(rects)

    return rect_frame
