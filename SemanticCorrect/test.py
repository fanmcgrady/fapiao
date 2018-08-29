import os

'''
seatNum = "11211E号"

seatNum = seatNum[0:2]+'车'+seatNum[3:]

print(seatNum)

xs ={
        'departCity':[29,74,247-29,128-74],
        'arriveCity':[425,68,649-425,132-68],
        'trainNumber':[230, 65, 433-230, 127-65],
        'invoiceDate':[0,163, 357,204-163],
        'seatNum':[392,164, 595-392, 210-164],
        'idNum':[0,343, 350,388-343],
        'passenger':[-1,-1,0,0],
        'price':[3,206, 215-3, 258-206],
        'ticketsNum':[34,40, 236-34,87-40]

        }
'''
xs ={
    'departCity': [48, 62, 270 - 48, 118 - 62],
    'arriveCity': [412, 61, 640 - 412, 116 - 61],
    'trainNumber': [264, 62, 434 - 264, 119 - 62],
    'invoiceDate': [24, 139, 393 - 24, 181 - 139],
    'seatNum': [408, 138, 568 - 408, 178 - 138],
    'idNum': [22, 276, 328 - 22, 314 - 276],
    'passenger': [328, 276, 478 - 328, 314 - 276],
    'price': [33, 177, 184 - 33, 216 - 177],
    'ticketsNum': [21, 10, 216 - 21, 76 - 10]

}

for c in xs:
    print(c)
print(xs)

