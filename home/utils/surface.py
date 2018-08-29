import os
import cv2
# import matplotlib.pyplot as pl
import fp

def detect(dset_root, file_name):
    raw_im = cv2.imread(os.path.join(dset_root, file_name), 1)

    # 初步矫正
    detect = fp.frame.surface.Detect()
    out_im = detect(raw_im)

    if fp.train_ticket.is_upside_down(out_im):
        std_out_im = fp.core.trans.rotate180(out_im)  # turn around if it's upside down
    else:
        std_out_im = out_im

    # 微调
    adjust = fp.frame.surface.Adjust()
    std_out_im = adjust(std_out_im)

    out_filename = file_name.replace('upload', 'out')

    cv2.imwrite(os.path.join(dset_root, out_filename), std_out_im)

    blue_ticket = fp.train_ticket.is_blue(out_im)  # blue or red ticket

    return out_filename, '蓝底车票' if blue_ticket else '红底车票'

if __name__ == '__main__':
    detect('../allstatic', 'upload/tr3.jpg')


