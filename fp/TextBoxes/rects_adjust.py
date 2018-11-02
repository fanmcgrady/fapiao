import os, sys
import cv2
import numpy as np
import glob
import pandas


##  centre of gravity
def calc_center(bn_img):
    M = cv2.moments(bn_img)
    try:
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
    except ZeroDivisionError as e:
        cx = int(bn_img.shape[1] / 2)
        cy = int(bn_img.shape[0] / 2)
    return cx, cy

def read_rects(csv_file):
    df = pandas.read_csv(csv_file, header=None, sep=',', names=["x", "y", "width", "height", "confidence"])

    rects = list()
    for i in range(1, len(df)):
        x = int(df["x"][i])
        y = int(df["y"][i])
        w = int(df["width"][i])
        h = int(df["height"][i])
        rects.append([x, y, w, h])
    return rects


def write_rects(rects, csv_file):
    dp = pandas.DataFrame(rects, columns=["x", "y", "width", "height"])
    dp.to_csv(csv_file)

# scan a line on a direction
def _line_scan_1eft(bn_img, pts, max_len, thres):
    cnt = 0
    step = int(max_len / 8)
    while (True):
        if pts[0][0] <= 4 or pts[1][0] <= 4 or cnt > max_len or \
                np.mean(bn_img[pts[0][1]:pts[1][1], pts[0][0] - step:pts[0][0]] / 255) < thres:
            break
        pts[0][0] -= step
        pts[1][0] -= step
        cnt += step
    return pts


def _line_scan_right(bn_img, pts, max_len, thres):
    cnt = 0
    step = int(max_len / 8)
    while (True):
        if pts[0][0] > bn_img.shape[1] - 4 or pts[1][0] > bn_img.shape[1] - 4 or cnt > max_len or \
                np.mean(bn_img[pts[0][1]:pts[1][1], pts[0][0]:pts[0][0] + step] / 255) < thres:
            break
        pts[0][0] += step
        pts[1][0] += step
        cnt += step
    return pts


def _local_threshold(gray_image, rcts):
    bn_image = np.zeros(gray_image.shape)
    for rct in rcts:
        _rct = rct.copy()
        ex_len = rct[3] * 2
        _rct[0] = max(0, rct[0] - ex_len)
        _rct[1] = max(0, rct[1] - ex_len)
        _rct[2] = min(gray_image.shape[1] - _rct[0] - 1, rct[2] + 2 * ex_len)
        _rct[3] = min(gray_image.shape[0] - _rct[1] - 1, rct[3] + 2 * ex_len)

        roi = gray_image[_rct[1]:_rct[1] + _rct[3], _rct[0]:_rct[0] + _rct[2]]
        blur = cv2.GaussianBlur(roi, (3, 3), 0)
        ret, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        bn_image[_rct[1]:_rct[1] + _rct[3], _rct[0]:_rct[0] + _rct[2]] = th
    return bn_image


def rects_adjust(im, rcts):
    if im.dtype != np.uint8:
        im = im.astype(np.uint8)
    if im.shape[2] != 1:
        gray_image = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = im

    bn_img = _local_threshold(gray_image, rcts)
    kernel = np.ones((5, 5), np.uint8)
    bn_img = cv2.dilate(bn_img, kernel, iterations=1)  
    _rcts = np.array(rcts).copy()
    for i in range(len(_rcts)):
        r = _rcts[i].astype(int)
        rgn = bn_img[r[1]:r[1] + r[3], r[0]:r[0] + r[2]].copy()
        cx, cy = calc_center(rgn)
        _rcts[i][0] += (cx - int(r[2] / 2))
        _rcts[i][1] += (cy - int(r[3] / 2))

    dirc = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]])
    for i in range(len(_rcts)):
        r = _rcts[i].astype(int)
        left = np.array([[r[0], r[1]], [r[0], r[1] + r[3]]])
        right = np.array([[r[0] + r[2], r[1]], [r[0] + r[2], r[1] + r[3]]])
        # up = np.array([[r[0],r[1]],[r[0]+r[2],r[1]]])
        # bottom = np.array([[r[0],r[1]+r[3]],[r[0]+r[2],r[1]+r[3]]])

        _rl = r.copy()
        left = _line_scan_1eft(bn_img, left, r[3] * 2, 0.2)
        _rl[2] += r[0] - left[0][0]
        _rl[0] = left[0][0]

        _rr = r.copy()
        right = _line_scan_right(bn_img, right, r[3] * 2, 0.2)
        _rr[2] = right[0][0] - r[0]

        r[0] = _rl[0]
        r[2] = _rr[0] + _rr[2] - r[0]

    return _rcts.tolist()


def drawboxes(image, rects):
    for i in range(len(rects)):
        cv2.rectangle(image, (rects[i][0], rects[i][1]), \
                      (rects[i][0] + rects[i][2], rects[i][1] + rects[i][3]), (255, 0, 0), 2)


if __name__ == "__main__":
    print('args: image_file_path[option]')
    if len(sys.argv) == 2:
        image_path = sys.argv[1]
    else:
        image_path = '/home/gaolin/TextBoxes/data/train_ticket'

    im_names = glob.glob(os.path.join(image_path, "*.jpg"))
	
    for im_name in im_names: 	
        print(im_name)
        cvs_file_tbx = im_name.replace('.jpg', '_tb.csv')
        im = cv2.imread(im_name, 1)
        
        rcts_tbx = read_rects(cvs_file_tbx)
        # rcts_fus = rects_fusion_simple(rcts_tbx,rcts_ipd,im.shape[:2])
        rcts_adj = rects_adjust(im, rcts_tbx)
       
        im_c = im.copy()
        drawboxes(im_c, rcts_tbx)
        sv_name = im_name.replace('.jpg', '_tbx.jpg')
        cv2.imwrite(os.path.join(os.path.dirname(sv_name),
                                 'result', os.path.basename(sv_name)), im_c)

        im_c = im.copy()
        drawboxes(im_c, rcts_adj)
        sv_name = im_name.replace('.jpg', '_adj.jpg')
        cv2.imwrite(os.path.join(os.path.dirname(sv_name),
                                 'result', os.path.basename(sv_name)), im_c)
