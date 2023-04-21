### distortion calculations

import math
# points

xcam = 277
ycam = 0

real_points = [(),(),(),(),()]


for tup in real_points:
    x = tup[0]
    y=tup[1]
    angle = math.atan((y-ycam)/(math.abs(x-xcam))) + 55

    xu = 
