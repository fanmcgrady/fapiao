import numpy as np
import cv2

def line_angle(line):
    '''return angle range [-90., 90.)'''
    x0, y0, x1, y1 = line
    ang = cv2.fastAtan2(y1 - y0, x1 - x0)
    if ang < 90.:
        return ang
    elif 90. <= ang < 270.:
        return ang - 180.
    elif 270. <= ang:
        return ang - 360.



def line_length(line):
    x0, y0, x1, y1 = line
    return np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

def cos_intersect_angle(line0, line1):
    '''Get the cosine of the intersection angle 
    formed by two lines'''
    x0, y0, x1, y1 = line0
    x2, y2, x3, y3 = line1
    v0 = np.array([x1 - x0, y1 - y0], np.float64)
    v0 /= np.linalg.norm(v0)
    v2 = np.array([x3 - x2, y3 - y2], np.float64)
    v2 /= np.linalg.norm(v2)
    return np.dot(v0, v2)

def intersect_point(line0, line1):
    '''Get the intersection point of two lines'''
    x0, y0, x1, y1 = line0
    x2, y2, x3, y3 = line1
    v0 = np.array([x0, y0, 1], np.float64)
    v1 = np.array([x1, y1, 1], np.float64)
    v2 = np.array([x2, y2, 1], np.float64)
    v3 = np.array([x3, y3, 1], np.float64)
    l0 = np.cross(v0, v1)
    l1 = np.cross(v2, v3)
    cp = np.cross(l0, l1)
    return cp[0] / cp[2], cp[1] / cp[2]

def intersect_point_dist(line, cross_point):
    x0, y0, x1, y1 = line
    xp, yp = cross_point
    if min(x0, x1) <= xp <= max(x0, x1) and \
            min(y0, y1) <= yp <= max(y0, y1):
        return 0
    else:
        d0 = np.linalg.norm([xp - x0, yp - y0])
        d1 = np.linalg.norm([xp - x1, yp - y1])
        return min(d0, d1)


def point_line_distance(p1, p2, p3):
    '''line end-point p1 p2, p3 is the third point to check'''
    if not isinstance(p1, np.ndarray) or p1.dtype != np.float32:
        p1 = np.array(p1, dtype=np.float32)
    if not isinstance(p2, np.ndarray) or p2.dtype != np.float32:
        p2 = np.array(p2, dtype=np.float32)
    if not isinstance(p3, np.ndarray) or p3.dtype != np.float32:
        p3 = np.array(p3, dtype=np.float32)
    return np.abs(np.cross(p2 - p1, p3 - p1)) / np.linalg.norm(p2 - p1)


def point_line_projection(p1, p2, p3):
    if not isinstance(p1, np.ndarray) or p1.dtype != np.float32:
        p1 = np.array(p1, dtype=np.float32)
    if not isinstance(p2, np.ndarray) or p2.dtype != np.float32:
        p2 = np.array(p2, dtype=np.float32)
    if not isinstance(p3, np.ndarray) or p3.dtype != np.float32:
        p3 = np.array(p3, dtype=np.float32)
    v = p2 - p1
    return v * np.dot(p3 - p1, v) / np.sum(v ** 2) + p1


def point_lineseg_distance(p1, p2, p3):
    '''
    line (p1, p2), third point p3
    If p3's projection is inside p1-p2, then the distance is perpendicular distance
    otherwise is the distance to end-point.
    
    distance = point-line distance,   if p3's projection inside p1-p2
               Eul-dist to endpoint,  else
    '''
    if not isinstance(p1, np.ndarray) or p1.dtype != np.float32:
        p1 = np.array(p1, dtype=np.float32)
    if not isinstance(p2, np.ndarray) or p2.dtype != np.float32:
        p2 = np.array(p2, dtype=np.float32)
    if not isinstance(p3, np.ndarray) or p3.dtype != np.float32:
        p3 = np.array(p3, dtype=np.float32)
    d = np.dot(p3 - p1, p2 - p1)
    t = np.sum((p2 - p1) ** 2)
    if d > t or d < 0:
        d13 = np.linalg.norm(p3 - p1)
        d23 = np.linalg.norm(p3 - p2)
        return np.min([d13, d23])
    else:
        return point_line_distance(p1, p2, p3)
