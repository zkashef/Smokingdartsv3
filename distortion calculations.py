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
b2 = []

for i in range(len(meas_x_pixel)):
    b += [actual_x_pixel[i] - meas_x_pixel[i]]
    b2 += [meas_x_pixel[i] - actual_x_pixel[i]]
b = np.array(b).T
b2 = np.array(b2).T



A = []
A2 = []

for j in range(len(meas_x_pixel)):
    x_diff = meas_x_pixel[j] - center[0] 
    y_diff = meas_y_pixel[j] - center[1]
    r = radius[j]
    row = [x_diff*r**2, x_diff*r**4, x_diff*r**6, r**2 + 2*(x_diff)**2, 2*x_diff*y_diff]
    x_diff2 =  actual_x_pixel[j] - center[0] 
    
    row2 = [x_diff2*r**2]#, x_diff2*r**4, x_diff2*r**6]#, x_diff2*r**6, x_diff2*r**8]
    A+=[row]
    A2+=[row2]

A = np.array(A)
A2 = np.array(A2)

#coeff = np.linalg.lstsq(A, b)

prod = np.matmul(A.T, A)
inv = np.linalg.inv(prod)
coeff = np.matmul(np.matmul(inv, A.T), b)


prod2 = np.matmul(A2.T, A2)
inv2 = np.linalg.inv(prod2)
coeff2 = np.matmul(np.matmul(inv2, A2.T), b2)


print(coeff)

k1 = coeff[0]
k2 = coeff[1]
k3 = coeff[2]
p1 = coeff[3]
p2 = coeff[4]


print(coeff2)
k12 = coeff2[0]
#k22 = coeff2[1]
#k32 = coeff2[2]
#k42 = coeff2[3]


#np.save('/dist_coefs.npy', coeff)





test_x = 1600
test_y = 500

test_x_diff =  test_x - center[0] 
test_y_diff = test_y - center[1]
test_r = math.sqrt(test_x_diff**2 + test_y_diff**2)

xu_pred = test_x + test_x_diff*test_r**2 * k1 + test_x_diff*test_r**4 * k2 + test_x_diff*test_r**6 * k3 + (test_r**2 + 2*(test_x_diff)**2) * p1 + 2*test_x_diff*test_y_diff*p2


x = 81
y= 90
angle = math.atan((y-ycam)/(abs(x-xcam))) * 180/math.pi + 44.5

#angle = 89
actual_xu = angle/89 * 1920

print("actual" + str(actual_xu))
print("Brown-Conrady: " + str(xu_pred))







xu_pred2 =   center[0] + (test_x-center[0])/(1 + test_r**2*k12)# + test_r**4*k22 + test_r**6*k32)# + test_r**8*k42)





print("division: " + str(xu_pred2))


    
