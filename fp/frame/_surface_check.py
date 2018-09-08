import numpy as np
import cv2

def is_crop_ready(image, pixval_tolerance=0.98, area_tolerance=0.1):
    assert isinstance(image, np.ndarray)
    if len(image.shape) == 3:
        image = image[:, :, 1]
    assert len(image.shape) == 2
    h, w = image.shape[0], image.shape[1]
    pix_th = int(np.max(image) * pixval_tolerance)
    #print('pix_th', pix_th, np.max(image))
    _, bim = cv2.threshold(image, pix_th, 255, cv2.THRESH_BINARY)
    ys = np.linspace(0, h, 10)
    xs = np.linspace(0, w, 10)
    clear_count = 0
    for y0, y1 in zip(ys[:-1], ys[1:]):
        y0, y1 = int(y0), int(y1)
        for x0, x1 in zip(xs[:-1], xs[1:]):
            x0, x1 = int(x0), int(x1)
            bg_count = cv2.countNonZero(bim[y0:y1, x0:x1])
            pix_count = (x1 - x0) * (y1 - y0)
            #print('{:.2f}, '.format(bg_count/pix_count), end='')
            if bg_count >= 0.98 * pix_count:
                clear_count += 1
        #print(' ')
    #print('bg ratio: {:.4f}'.format(clear_count/100))
    if clear_count >= 20:
        return False
    return True
    
    