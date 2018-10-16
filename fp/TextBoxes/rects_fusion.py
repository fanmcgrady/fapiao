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

# dirc:  numpy array (x,y): [-1,0],[0,-1],[1,0],[0,1]
# pt: numpy array start point [x,y]
# scan a point on a direction
def _line_scan(bn_img, dirc, pt, max_len):
    val = bn_img[pt[1], pt[0]]
    cnt = 0
    while (True):
        if pt[0] > bn_img.shape[1] or pt[1] > bn_img.shape[0] or \
                pt[0] <= 1 or pt[1] <= 1 or cnt > max_len or bn_img[pt[1], pt[0]] < val:
            break
        pt += dirc
        cnt += 1
    return pt

# scan a line on a direction
def _line_scan_1eft(bn_img, dirc, pts, max_len):
    val = bn_img[pts[0][1]:pts[1][1], pts[0][0]]
    cnt = 0
    while (True):
        if pt[0] > bn_img.shape[1] or pt[1] > bn_img.shape[0] or \
                pt[0] <= 1 or pt[1] <= 1 or cnt > max_len or bn_img[pt[1], pt[0]] < val:
            break
        pt += dirc
        cnt += 1
    return pt


def _local_threshold(gray_image, rcts):
    bn_image = np.zeros(gray_image.shape)
    for rct in rcts:
        roi = gray_image[rct[1]:rct[1] + rct[3], rct[0]:rct[0] + rct[2]]
        blur = cv2.GaussianBlur(roi, (3, 3), 0)
        ret, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        bn_image[rct[1]:rct[1] + rct[3], rct[0]:rct[0] + rct[2]] = th
    return bn_image

# fusion two sets of rects
# rcts: list of [x,y,width,height]
def rects_fusion_simple(rcts_tbx, rcts_ipd, bn_img_shape):
    '''
    step 1: move rcts_tbx as one
    '''
    bn_img = np.zeros(bn_img_shape)
    for i in range(len(rcts_ipd)):
        r = rcts_ipd[i]
        bn_img[r[1]:r[1] + r[3], r[0]:r[0] + r[2]] = 255
        
    _rcts_tbx = np.array(rcts_tbx).copy()
    for i in range(len(_rcts_tbx)):
        r = _rcts_tbx[i]
        rgn = bn_img[r[1]:r[1] + r[3], r[0]:r[0] + r[2]].copy()
        cx, cy = calc_center(rgn)
        _rcts_tbx[i][0] += (cx - int(r[2] / 2))
        _rcts_tbx[i][1] += (cy - int(r[3] / 2))

    '''
    step 2: move four sides individually
    '''
    dirc = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]])
    for i in range(len(_rcts_tbx)):
        r = _rcts_tbx[i]
        left = np.array([r[0], r[1] + int(r[3] / 2)])
        up = np.array([r[0] + int(r[2] / 2), r[1]])
        right = np.array([min(r[0] + r[2], bn_img.shape[1] - 1), r[1] + int(r[3] / 2)])
        bottom = np.array([r[0] + int(r[2] / 2), min(r[1] + r[3], bn_img.shape[0] - 1)])

        _rl = r.copy()
        if bn_img[left[1], left[0]] == 255:
            left = _line_scan(bn_img, dirc[0], left, r[3])
            _rl[2] += r[0] - left[0]
            _rl[0] = left[0] 
       
        _rr = r.copy()
        if bn_img[right[1], right[0]] == 255:
            right = _line_scan(bn_img, dirc[2], right, r[3])
            _rr[2] = right[0] - r[0]

        '''
        if bn_img[up[1],up[0]]==255:
            up = _line_scan(bn_img,dirc[1],up,r[3])
            r[3] += r[1]-up[1]
            r[1] = up[1]

        if bn_img[bottom[1],bottom[0]]==255:
            bottom = _line_scan(bn_img,dirc[3],bottom,r[3])
            r[3] += bottom[1]-r[1]   
        '''
        r[0] = _rl[0]
        r[2] = _rr[0] + _rr[2] - r[0]
    
    return _rcts_tbx.tolist()


def drawboxes(image, rects):
    for i in range(len(rects)):
        cv2.rectangle(image, (rects[i][0], rects[i][1]), \
                      (rects[i][0] + rects[i][2], rects[i][1] + rects[i][3]), (255, 0, 0), 2)


if __name__ == "__main__":
    print('args: image_file_path[option]')
    if len(sys.argv) == 2:
        image_path = sys.argv[1]
    else:
        image_path = '/home/gaolin/TextBoxes/data/fapiao_scan'

    im_names = glob.glob(os.path.join(image_path, "*.jpg"))

    for im_name in im_names:
        print(im_name)
        cvs_file_tbx = im_name.replace('.jpg', '_tb.csv')
        cvs_file_ipd = im_name.replace('.jpg', '.csv')
        im = cv2.imread(im_name, 1)
        
        rcts_tbx = read_rects(cvs_file_tbx)
        rcts_ipd = read_rects(cvs_file_ipd)
        rcts_fus = rects_fusion_simple(rcts_tbx, rcts_ipd, im.shape[:2])
       
        im_c = im.copy()
        drawboxes(im_c, rcts_tbx)
        print("tbx", rcts_tbx)
        sv_name = im_name.replace('.jpg', '_tbx.jpg')
        cv2.imwrite(os.path.join(os.path.dirname(sv_name),
                                 'result', os.path.basename(sv_name)), im_c)

        im_c = im.copy()
        drawboxes(im_c, rcts_fus)
        print("fus", rcts_fus)
        sv_name = im_name.replace('.jpg', '._fus.jpg')
        cv2.imwrite(os.path.join(os.path.dirname(sv_name),
                                 'result', os.path.basename(sv_name)), im_c)

  
        im_c = im.copy()
        drawboxes(im_c, rcts_ipd)
        print("ipd", rcts_ipd)
        sv_name = im_name.replace('.jpg', '_ipd.jpg')
        cv2.imwrite(os.path.join(os.path.dirname(sv_name),
                                 'result', os.path.basename(sv_name)), im_c)
