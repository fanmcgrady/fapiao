import os
import importlib
import cv2
import numpy as np
import torch
import torchvision
import yaml

from ..model import pascal_voc

importlib.reload(pascal_voc)
# from ..util import path
# importlib.reload(path)
from ..core import stats

importlib.reload(stats)
from . import _template_remap as remap

importlib.reload(remap)
from ..util import visualize

importlib.reload(visualize)


def xml_info(xmlfile):
    '''use pascal voc as named rects'''
    xml_info = pascal_voc.parse_xml(xmlfile)
    objects = xml_info['objects']
    named_rects = {item['name']: item['bndbox'] for item in objects}
    std_size = xml_info['shape'][1], xml_info['shape'][0]
    return named_rects, std_size


def normalized_anchors(named_rects, std_size, keys):
    anchors = []
    for key in keys:
        code = remap.align_code(key)
        rect = named_rects[key]
        anchors.append(remap.ReMap(code, std_size).to_anchor(rect))

    anchors = torch.stack(anchors)
    center = torch.mean(anchors[:, :2], dim=0)
    anchors[:, :2] -= center
    return anchors, center


def sort_keys(keys):
    striped_keys = [key.strip('_') for key in keys]
    sorted_idx = sorted(range(len(striped_keys)), key=lambda k: striped_keys[k])
    sorted_keys = [keys[i] for i in sorted_idx]
    return sorted_keys


def _vector_update(vec_mean, vec_std, new_vec, count):
    assert len(vec_mean) == len(vec_std) and len(vec_mean) == len(new_vec)
    for i in range(len(vec_mean)):
        vec_mean[i] = stats.online_mean(vec_mean[i], new_vec[i], count)
        vec_std[i] = stats.online_std(vec_mean[i], vec_std[i], new_vec[i], count)


def tensor_to_list(tensor):
    if tensor.device != torch.device('cpu'):
        return tensor.detach().cpu().numpy().tolist()
    else:
        return tensor.detach().numpy().tolist()


class TemplateData(object):
    def __init__(self, keys=None, debug=False):
        if keys is not None:
            keys = sort_keys(keys)
        self.keys = keys
        self.reset()
        self.count = 0
        self.debug = dict() if debug else None

    def load(self, filename):
        assert isinstance(filename, str)
        if filename[-5:].lower() != '.yaml':
            filename = filename + '.yaml'
        assert os.path.isfile(filename)

        with open(filename, 'r') as fp:
            dict_load = yaml.load(fp.read())
            fp.close()

        self.keys = sort_keys(dict_load['keys'])
        self.center_mean = torch.tensor(dict_load['center_mean'])
        self.center_std = torch.tensor(dict_load['center_std'])
        self.anchors_mean = torch.tensor(dict_load['anchors_mean'])
        self.anchors_std = torch.tensor(dict_load['anchors_std'])
        self.count = dict_load['count']

    def save(self, filename):
        assert isinstance(filename, str)
        if filename[-5:].lower() != '.yaml':
            filename = filename + '.yaml'

        with open(filename, 'w') as fp:
            dict_save = dict(keys=self.keys,
                             center_mean=tensor_to_list(self.center_mean),
                             center_std=tensor_to_list(self.center_std),
                             anchors_mean=tensor_to_list(self.anchors_mean),
                             anchors_std=tensor_to_list(self.anchors_std),
                             count=self.count)
            fp.write(yaml.dump(dict_save))
            fp.close()

    def reset(self):
        self.center_mean = None
        self.center_std = None
        self.anchors_mean = None
        self.anchors_std = None
        self.count = 0

    def fit(self, xmlfiles, alpha=3.0, min_anchors_std=0.006, min_center_std=0.01):
        assert len(xmlfiles) > 0
        if self.keys is None:
            named_rects, _ = xml_info(xmlfiles[0])
            self.keys = sort_keys(list(named_rects.keys()))
        keys_set = set(self.keys)

        anchorx = []
        centers = []
        for xml in xmlfiles:
            named_rects, std_size = xml_info(xml)
            if set(named_rects.keys()) != keys_set:
                print('Invalid keys in {}:'.format(xml))
                print('  named_rect.keys: {}'.format(named_rects.keys()))
                print('  keys_set       : {}'.format(keys_set))
            assert set(named_rects.keys()) == keys_set
            anchors, center = normalized_anchors(named_rects, std_size, self.keys)
            anchorx.append(anchors)
            centers.append(center)
        anchorx = torch.stack(anchorx)
        centers = torch.stack(centers)
        if self.debug is not None:
            self.debug['anchorx'] = anchorx
            self.debug['centers'] = centers

        self.anchors_mean = anchorx.mean(dim=0)
        anchors_std = alpha * anchorx.std(dim=0)
        anchors_std[anchors_std < min_anchors_std] = min_anchors_std
        self.anchors_std = anchors_std

        self.center_mean = centers.mean(dim=0)
        center_std = alpha * centers.std(dim=0)
        center_std[center_std < min_center_std] = min_center_std
        self.center_std = center_std
        return True

    def update(self, new_anchors, succeed):
        assert new_anchors is not None
        n_anchors = len(self.anchors_mean)
        assert len(new_anchors) == n_anchors

        new_center = torch.mean(new_anchors[:, :2], dim=0)
        new_anchors[:, :2] -= new_center

        # todo : update center
        _vector_update(self.center_mean, self.center_std, new_center, self.count)

        for j in range(n_anchors):
            if succeed[j] == 0:
                continue
            new_anchor = new_anchors[j]
            _vector_update(self.anchors_mean[j], self.anchors_std[j], new_anchor, self.count)

        self.count += 1

    def named_rects(self, image_size):
        anchors = self.anchors_mean.clone()
        anchors[:, :2] += self.center_mean
        return {key: remap.ReMap(remap.align_code(key), image_size).to_rect(anchor)
                for key, anchor in zip(self.keys, anchors)}


def draw_anchorx_centers(keys, anchorx, centers, image_size):
    assert len(anchorx) == len(centers)
    n_samples = len(anchorx)
    n_items = len(keys)
    W, H = image_size
    im = np.zeros((H, W, 3), dtype=np.uint8)
    colors = visualize.fixed_color_array(n_items)
    cx, cy = centers.mean(dim=0)
    for i in range(n_samples):
        x, y = centers[i]
        x, y = int(x * W), int(y * H)
        cv2.circle(im, (x, y), 1, (255, 255, 255), thickness=-1)
        for j in range(n_items):
            code = remap.align_code(keys[j])
            x, y, w, h = remap.ReMap(code, image_size).to_rect(anchorx[i][j], False)
            p0 = int(x + W * cx), int(y + H * cy)
            p1 = int(x + W * cx + w), int(y + H * cy + h)
            p3 = int(x + W * cx + w * 0.5), int(y + H * cy + h * 0.5)
            cv2.rectangle(im, p0, p1, colors[j])
            cv2.circle(im, p3, 1, colors[j], thickness=-1)
    return im
