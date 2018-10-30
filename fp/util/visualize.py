import os
import numpy as np
import cv2
import matplotlib.pyplot as pl

from . import path

def _make_canvas(image, image_shape):
    if image is not None:
        assert isinstance(image, np.ndarray)
        img_shape_len = len(image.shape)
        assert img_shape_len == 2 or img_shape_len == 3
        if img_shape_len == 2:
            return cv2.merge((image, image, image))
        else:
            return image.copy()
    else:
        assert image_shape is not None
        assert isinstance(image_shape, tuple) or isinstance(image_shape, list)
        img_shape_len = len(image_shape)
        assert img_shape_len == 2 or img_shape_len == 3
        if img_shape_len == 2:
            image_shape = (*image_shape, 3)
        return np.zeros(image_shape, np.uint8)
    raise NotImplemented


def rects(image, rects, types=None, image_shape=None):
    image = _make_canvas(image, image_shape)
    if types is None:
        for x, y, w, h in rects:
            p0 = int(round(x)), int(round(y))
            p1 = int(round(x + w)), int(round(y + h))
            cv2.rectangle(image, p0, p1, (255, 0, 0), thickness=2)
    else:
        n_color = np.max(types) + 1
        np.random.seed(5)
        colors = np.random.randint(256, size=(n_color, 3))
        for (x, y, w, h), type_ in zip(rects, types):
            color = tuple(colors[int(type_), :].tolist())  # Wired! must use .tolist()
            p0 = int(round(x)), int(round(y))
            p1 = int(round(x + w)), int(round(y + h))
            cv2.rectangle(image, p0, p1, color, thickness=2)
    return image

def named_rects(image, named_rects, image_shape=None):
    image = _make_canvas(image, image_shape)
    np.random.seed(0)
    for name, (x, y, w, h) in named_rects.items():
        if w * h == 0:
            continue
        p0 = int(x), int(y)
        p1 = int(x + w), int(y + h)
        r = np.random.randint(256)
        g = np.random.randint(256)
        b = np.random.randint(256)
        cv2.rectangle(image, p0, p1, (r, g, b), thickness=3)
        cv2.putText(image, name, (int(x), int(y) - 6), \
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (155, 155, 155), 2, cv2.LINE_AA)
    return image


def points(image, points, image_shape=None, radius=1):
    image = _make_canvas(image, image_shape)
    for x, y in points:
        x, y = int(x), int(y)
        cv2.circle(image, (x, y), radius, (255, 0, 0), -1)
    return image

def roi_cut(image, roi):
    x, y, w, h = roi
    return image[y:y + h, x:x + w]

def fixed_color_array(n):
    np.random.seed(0)
    color_array = []
    for i in range(n):
        r = np.random.randint(256)
        g = np.random.randint(256)
        b = np.random.randint(256)
        color_array.append([r, g, b])
    return color_array

def batch_display(images, fig_size, cols=2, cmap=None):
    n = len(images)
    rows = int(np.ceil(n / cols))
    pl.figure(figsize=fig_size)
    for i in range(n):
        image = images[i]
        pl.subplot(rows, cols, i + 1)
        pl.imshow(image, cmap=cmap)
    pl.show()


class PathImages(object):
    def __init__(self, image_paths, colored=1):
        self.image_paths = image_paths
        self.colored = int(colored)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        assert isinstance(idx, int)
        return cv2.imread(self.image_paths[idx], self.colored)


class FolderDisplay(object):
    IMAGEFILE_EXTS = ['.jpg', '.png', '.bmp']

    def __init__(self, folder, fig_size=(16, 16), cols=2, cmap=None):
        self.image_paths = path.files_in_dir(folder,
                                             exts=self.IMAGEFILE_EXTS,
                                             include_dir=True)
        self.fig_size = fig_size
        self.cols = cols
        self.cmap = cmap
        if len(self.image_paths) == 0:
            print('Warning: no images found!')

    def __getitem__(self, idx):
        if len(self.image_paths) == 0:
            print('Warning: No images to display!')
            return
        if isinstance(idx, int):
            assert idx < len(self.image_paths)
            selected_path = [self.image_paths[idx]]
        if isinstance(idx, slice):
            selected_path = self.image_paths[idx]
        images = PathImages(selected_path, colored=1)
        batch_display(images, self.fig_size, self.cols, self.cmap)

    def __call__(self, idx):
        return self.image_paths[idx]