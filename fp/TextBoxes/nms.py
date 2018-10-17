from __future__ import division
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.geometry import MultiPoint

def polygon_from_list(line):
    """
    Create a shapely polygon object from gt or dt line.
    """
    # polygon_points = [float(o) for o in line.split(',')[:8]]
    polygon_points = np.array(line).reshape(4, 2)
    polygon = Polygon(polygon_points).convex_hull
    return polygon

def polygon_iou(list1, list2):
    """
    Intersection over union between two shapely polygons.
    """
    polygon_points1 = np.array(list1).reshape(4, 2)
    poly1 = Polygon(polygon_points1).convex_hull
    polygon_points2 = np.array(list2).reshape(4, 2)
    poly2 = Polygon(polygon_points2).convex_hull
    union_poly = np.concatenate((polygon_points1, polygon_points2))
    if not poly1.intersects(poly2):  # this test is fast and can accelerate calculation
        iou = 0
    else:
        try:
            inter_area = poly1.intersection(poly2).area
            # union_area = poly1.area + poly2.area - inter_area
            union_area = MultiPoint(union_poly).convex_hull.area
            if union_area == 0:
                return 1
            iou = float(inter_area) / union_area
        except shapely.geos.TopologicalError:
            print('shapely.geos.TopologicalError occured, iou set to 0')
            iou = 0
    return iou


def nms(boxes, threshold):
    # print 'boxes',boxes
    nms_flag = [True] * len(boxes)

    for i, b in enumerate(boxes):
        if not nms_flag[i]:
            continue
        else:
            for j, a in enumerate(boxes):
                if a == b:
                    continue
                if not nms_flag[j]:
                    continue
                rec1 = b[0:8]
                rec2 = a[0:8]
                box_i = [b[0], b[1], b[4], b[5]]
                box_j = [a[0], a[1], a[4], a[5]]
                poly1 = polygon_from_list(b[0:8])
                poly2 = polygon_from_list(a[0:8])
                polygon_points1 = np.array(rec1).reshape(4, 2)
                # poly1 = Polygon(polygon_points1).convex_hull
                poly1 = Polygon(polygon_points1)
                polygon_points2 = np.array(rec2).reshape(4, 2)
                # poly2 = Polygon(polygon_points2).convex_hull
                poly2 = Polygon(polygon_points2)
                if poly1.area == 0:
                    nms_flag[i] = False
                    continue
                if poly2.area == 0:
                    nms_flag[j] = False
                    continue
                iou = polygon_iou(rec1, rec2)
                if iou > threshold:
                    if b[8] > a[8]:
                        nms_flag[j] = False
                    elif b[8] == a[8] and poly1.area > poly2.area:
                        nms_flag[j] = False
                    elif b[8] == a[8] and poly1.area <= poly2.area:
                        nms_flag[i] = False
                        break
    return nms_flag
