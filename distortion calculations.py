### distortion calculations

import math
# points

xcam = 286
ycam = 0

real_points = [(-67.5, 59)]#,(),(),(),()]


for tup in real_points:
    x = tup[0]
    y=tup[1]
    angle = math.atan((y-ycam)/(abs(x-xcam))) * 180/math.pi + 55

    xu = angle/110 * 1920

    print(xu)
