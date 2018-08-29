import os
import numpy as np
import xml.dom.minidom

KEYS = ['folder', 'filename', 'path']

def _element_value(node, key):
    return node.getElementsByTagName(key)[0].childNodes[0].data
    
def parse_xml(xml_file):
    info = {}
    DomTree = xml.dom.minidom.parse(xml_file)  
    annotation = DomTree.documentElement  
  
    for _key in KEYS:
        info[_key] = _element_value(annotation, _key)
        
    size = annotation.getElementsByTagName('size')[0]
    img_w = int(_element_value(size, 'width'))
    img_h = int(_element_value(size, 'height')) 
    img_c = int(_element_value(size, 'depth'))
    info['shape'] = img_h, img_w, img_c

    objects = annotation.getElementsByTagName('object')
    objects_info = []
    for _object in objects:  
        # print objects  
        object_name = _element_value(_object, key='name') #namelist[0].childNodes[0].data  
        #print("{:16s}".format(objectname), end='')
        bndbox = _object.getElementsByTagName('bndbox')[0]
        x = int(_element_value(bndbox, 'xmin'))  
        y = int(_element_value(bndbox, 'ymin'))  
        w = int(_element_value(bndbox, 'xmax')) - x 
        h = int(_element_value(bndbox, 'ymax')) - y  
        #print("{:4d},{:4d},{:4d},{:4d}".format(x1, y1, w, h))
        objects_info.append(dict(name=object_name, bndbox=(x,y,w,h)))
    info['objects'] = objects_info
    return info



    
def image_shape(info):
    return info['shape']

def image_name(info):
    return info['filename']

def image_folder(info):
    return info['folder']