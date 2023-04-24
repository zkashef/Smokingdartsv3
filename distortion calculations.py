### distortion calculations

import math
import matplotlib.pyplot as plt
import numpy as np
# points

xcam = 287
ycam = 0

real_points = [(-1, -28), (-95, -41.5), (-2, -168), (-119, -119), (-93.5, -46), (81, 90)]#,(),(),(),()]

meas_x_pixel = [834, 816, 259, 580, 801, 1513]

meas_y_pixel = [615, 600, 599, 588, 503, 638]

actual_x_pixel = []







for tup in real_points:
    x = tup[0]
    y=tup[1]
    angle = math.atan((y-ycam)/(abs(x-xcam))) * 180/math.pi + 44.5

    xu = angle/89 * 1920

    actual_x_pixel += [xu]



center = (960, 540)
radius = []


for i in range(len(meas_x_pixel)):
    radius += [math.sqrt((meas_x_pixel[i]-center[0])**2 + (meas_y_pixel[i] - center[1])**2)]


b = []

for i in range(len(meas_x_pixel)):
    b += [actual_x_pixel[i] - meas_x_pixel[i]]
b = np.array(b).T



A = []

for j in range(len(meas_x_pixel)):
    x_diff = meas_x_pixel[j] - center[0] 
    y_diff = meas_y_pixel[j] - center[1]
    r = radius[j]
    row = [x_diff*r**2, x_diff*r**4, x_diff*r**6, r**2 + 2*(x_diff)**2, 2*x_diff*y_diff]
    A+=[row]

A = np.array(A)

#coeff = np.linalg.lstsq(A, b)

linAlg = np.matmul(A.T, A)

linAlg = np.linalg.inv(linAlg)

coeff = np.matmul(np.matmul(linAlg, A.T), b)

print(coeff)
k1 = coeff[0]
k2 = coeff[1]
k3 = coeff[2]
p1 = coeff[3]
p2 = coeff[4]

#np.save('/dist_coefs.npy', coeff)






test_x_diff = 1072 - center[0] 
test_y_diff = 604 - center[1]
test_r = math.sqrt(test_x_diff**2 + test_y_diff**2)

xu_pred = 1072 + test_x_diff*test_r**2 * k1 + test_x_diff*test_r**4 * k2 + test_x_diff*test_r**6 * k3 + (test_r**2 + 2*(test_x_diff)**2) * p1 + 2*test_x_diff*test_y_diff*p2


x = -47
y= 23
angle = math.atan((y-ycam)/(abs(x-xcam))) * 180/math.pi + 44.5

actual_xu = angle/89 * 1920

print(actual_xu)
print(xu_pred)


    
