# 678 * 434
import math

#blueTemplet = {'departCity': [48, 62, 222, 56], 'arriveCity': [412, 61, 228, 55], 'trainNumber': [264, 62, 170, 57], 'invoiceDate': [24, 139, 369, 42], 'seatNum': [408, 138, 160, 40], 'idNum': [22, 276, 306, 38], 'passenger': [328, 276, 150, 38], 'price': [33, 177, 151, 39], 'ticketsNum': [21, 10, 195, 66]}

def de_muban(muban, area_rate = 0.8):
    """
    :param muban: 模板字典，[key:[x,y,width,height]]
    :param area_rate: 新模板和旧模板面积比例，小于1为缩小
    :return: 新模板字典
    """
    for key in muban:
        lst = muban[key]
        x = lst[0]
        y = lst[1]
        width = lst[2]
        height = lst[3]
        rate = 1 - math.sqrt(area_rate)
        #de_width = rate * width / 2
        de_height = rate * height / 2
        new_x = x
        new_y = y + de_height
        new_width = width
        new_height = height - rate * height
        muban[key] = [new_x, new_y, new_width, new_height]

    return muban

#de_muban(blueTemplet)
