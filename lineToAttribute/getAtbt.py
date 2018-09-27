def compute(hang, muban):
    h, w = hang.shape
    m = muban.copy()
    for key in m:
        value = m[key]
        v_x = value[0]
        v_y = value[1]
        if v_x == -1 and v_y == -1:
            continue
        v_width = value[2]
        v_height = value[3]
        v_next_x = v_x + v_width
        v_next_y = v_y + v_height
        h_area = v_height * v_width
        max_area = 0
        for i in range(h):
            t = hang[i]
            x = t[0]
            y = t[1]
            width = t[2]
            height = t[3]
            next_x = x + width
            next_y = y + height

            x_1 = next_x - v_x
            x_2 = v_next_x - x
            y_1 = next_y - v_y
            y_2 = v_next_y - y
            if x_1 > 0 and x_2 > 0 and y_1 > 0 and y_2 > 0:
                area = min(x_1, x_2) * min(y_1, y_2)
                if (v_x < x and v_y < y and v_next_x > next_x and v_next_y > next_y):  # 模板完全包含行提取，返回模板
                    break
                elif (v_x > x and v_y > y and v_next_x < next_x and v_next_y < next_y):  # 行提取完全包含模板，返回行提取
                    max_area = area
                    m[key] = t
                elif width * height > h_area + 100:  # 行提取远大于又不包含，认为没有切好，返回模板（参数可能需要修改，身份证姓名行发现的问题）
                    break
                if max_area < area:  # 相交，结合模板与行提取返回
                    max_area = area
                    x_0 = min(v_x, x)
                    y_0 = min(v_y, y)
                    nx_0 = max(v_next_x, next_x)
                    ny_0 = max(v_next_y, next_y)

                    lst = [x_0, y_0, nx_0 - x_0, ny_0 - y_0]
                    m[key] = lst
        m[key][2] = int(m[key][2])
        m[key][3] = int(m[key][3])
    return m


'''
hang = [[210 424 120  17]
 [349 409 101  31]
 [ 90 408  37  20]
 [183 407   4  14]
 [251 406  17  13]
 [ 80 363 378  45]
 [135 333 287  23]
 [591 328  22  21]
 [175 328 302  14]
 [545 307  89  85]
 [ 48 290 390  30]
 [568 283  72  32]
 [531 283  26  16]
 [ 46 226  80  25]
 [168 225  65  24]
 [ 59 192 113  25]
 [292 189  36  24]
 [436 187 150  26]
 [143 156  30  24]
 [273 155  92  24]
 [196 155  47  25]
 [ 46 155  85  26]
 [434 154 120  25]
 [193 130  10  14]
 [144 129  41  15]
 [519 126  44  20]
 [103 124  28  20]
 [480 122  30  21]
 [295  87  98  29]
 [443  79  39  38]
 [ 62  79 179  40]
 [523  76  86  40]
 [609  41  26  23]
 [527  38  54  29]
 [ 46  37 151  29]]'''
