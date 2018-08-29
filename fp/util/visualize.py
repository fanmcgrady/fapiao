import numpy as np
import cv2

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
            p1 = int(round(x+w)), int(round(y+h))
            cv2.rectangle(image, p0, p1, (255,0,0), thickness=2)
    else:
        n_color = np.max(types) + 1
        np.random.seed(5)
        colors = np.random.randint(256, size=(n_color, 3))
        for (x, y, w, h), type_ in zip(rects, types):
            color = tuple(colors[int(type_), :].tolist()) # Wired! must use .tolist()
            p0 = int(round(x)), int(round(y))
            p1 = int(round(x+w)), int(round(y+h))
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
        cv2.putText(image, name, (int(x), int(y)-6), \
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (155,155,155), 2, cv2.LINE_AA)
    return image