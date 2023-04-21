### distortion calculations

import math
import matplotlib.pyplot as plt
# points

xcam = 286
ycam = 0

real_points = [(-67.5, 59)]#,(),(),(),()]

print(math.atan(21/22.5)*180/math.pi * 2)

for tup in real_points:
    x = tup[0]
    y=tup[1]
    angle = math.atan((y-ycam)/(abs(x-xcam))) * 180/math.pi + 55

    xu = angle/110 * 1920

    print(xu)



image_width = 1920
fov = 86
foc_len = (image_width/2)/math.tan((fov/2)*math.pi/180)
angles_cameras_to_darts = 0, 0




# Calculate Coordinates of Dart Relative to Scoring Area
#cam_dist = 381 #mm
x1, y1 = 286, 0
x2, y2 = 0, 286
board_radius = 228.6

"""if x1 > 0:
    angle_to_center1 = 180 + math.sin(y1/x1)*180/math.pi
else:
    angle_to_center1 =  0 + math.sin(y1/x1)*180/math.pi

if x2 > 0:
    angle_to_center2 =  180 + math.sin(y2/x2)*180/math.pi
else:
    angle_to_center2 =  0 + math.sin(y2/x2)*180/math.pi
"""
### for x1, y1 #####
if (x1 == 0 and y1 > 0):
    angle_to_center1 = 270
elif (x1 == 0 and y1 < 0):
    angle_to_center1 = 90
elif (x1 > 0):
    angle_to_center1 = 180 + math.atan(y1/x1)*180/math.pi
else:
    angle_to_center1 =  (360 + math.atan(y1/x1)*180/math.pi)%360

###### for x2, y2 #####
if (x2 == 0 and y2 > 0):
    angle_to_center2 = 270
elif (x2 == 0 and y2 < 0):
    angle_to_center2 = 90
elif (x2 > 0):
    angle_to_center2 = 180 + math.atan(y2/x2)*180/math.pi
else:
    angle_to_center2 =  (360 + math.atan(y2/x2)*180/math.pi)%360


total_angle1 = angle_to_center1 + (fov/2 - angles_cameras_to_darts[0]) 
total_angle2 = angle_to_center2 + (fov/2 - angles_cameras_to_darts[1])



if total_angle1 > 90 and total_angle1 < 270:
    slope1 = math.tan((total_angle1 - 180)*math.pi/180)
else:
    slope1 = math.tan((total_angle1)*math.pi/180)

if total_angle2 > 90 and total_angle2 < 270:
    slope2 = math.tan((total_angle2 - 180)*math.pi/180)

else:
    slope2 = math.tan((total_angle2)*math.pi/180)


x_dart = (x1*slope1 - y1 - x2*slope2 + y2 )/(slope1 - slope2)
y_dart = (x_dart - x1) * slope1 + y1
    
    
print("x coordinate(mm): " + str(x_dart))
print("y coordinate(mm): " + str(y_dart))


# Create Visualiation of Dart Board
fig, ax = plt.subplots() 
ax.set_xlim(-400, 400)
ax.set_ylim(-400, 400)

dart_board = plt.Circle((0, 0), board_radius, edgecolor='black', fill=False)
#dart_board = ax.pie([.05]*20)
dart = plt.Arrow(x_dart, y_dart, 15, 15, color='black')
bullseye = plt.Circle((0, 0), 10, edgecolor='black', fill=False)

camA = plt.Rectangle((x1, y1), 10, 10, edgecolor='black', fill=False, clip_on=False)
camB = plt.Rectangle((x2, y2), 10, 10, edgecolor='black', fill=False, clip_on=False) 




# Determine Score of Hit
radius = math.sqrt((x_dart**2)+(y_dart**2)) # find the radius

# solve for the angle
theta = math.atan(y_dart/x_dart) # in radians
angle = theta * (180/3.1415) # convert to degrees

# makes sure that the arctan angle is accurate for scoring
if x_dart < 0:
    angle = 180 + angle
print("angle: " + str(angle))

slice_map = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]
slice_key = int(((angle + 9)%360)//18)
slice_area = slice_map[slice_key]

print("score area: " + str(slice_area))
print("Radius: " + str(radius))
score = 0
channel = 0
if radius <= 5:
    score = 50
    print("Bullseye!!!")
elif radius > 5 and radius <= 15:
    score = 25
    print("Bull!!!")
elif radius > 15 and radius < 95:
    channel = 12
    score = slice_area
elif radius >= 95 and radius <= 105:
    score = 3*slice_area
    channel = 3
    print("Triple Score!!!")
elif radius > 105 and radius <160:
    channel = 11
    score = slice_area
elif radius >= 160 and radius <=170:
    score = 2*slice_area
    channel = 2
    print("Double Score!!!")
    
elif radius > 170:
    score = 0
    print("Missed. Try Again.")
else:
    score = slice_area
    print("Nice hit!!!")
print("The score is: " + str(score))



ax.add_patch(dart_board)
ax.add_patch(dart)
ax.add_patch(bullseye)
ax.add_patch(camA)
ax.add_patch(camB)

leg_Cam1_Dart = ax.axline((x1, y1), slope= slope1)
leg_Cam2_Dart = ax.axline((x2, y2), slope = slope2)

ax.plot(x_dart, y_dart)



plt.show()
