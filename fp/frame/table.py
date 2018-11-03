import os
import sys
import importlib
import numpy as np
import cv2
import sklearn
import sklearn.cluster

from ..core import rectangle


# todo: make same left border
class TableParser(object):
    def __init__(self):
        self.rows = None

    def __call__(self, textlines):
        mean_height = np.mean([rect[3] for rect in textlines])
        eps = mean_height * 1.1
        ys = np.array([rect[1] for rect in textlines]).reshape(-1, 1)
        # print(mean_height)
        core_samples, labels = sklearn.cluster.dbscan(ys, eps=eps, min_samples=1)
        # print(labels)
        self.num_rows = np.max(labels) + 1
        rows = np.zeros((self.num_rows, 4))
        for i in range(self.num_rows):
            rows[i] = rectangle.bounding_rect(textlines[labels == i])
        # print(rows)
        self.rows = rows
        return rows
