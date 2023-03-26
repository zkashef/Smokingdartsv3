# import libraries
import cv2
import matplotlib.pyplot as plt
import os
from skimage.metrics import structural_similarity as compare_ssim
import numpy as np
import math


def capture_image(camera, image_name, path):
    ret, img = camera.read() # Read an image from camera
    image_name = image_name + ".jpeg"
    cv2.imwrite(os.path.join(path, image_name), img)
    camera.release()
    print(image_name + " captured!")



def show_diff_image(imageA, imageB):
    grayA = cv2.cvtColor(imageA, cv2.COLOR_RGB2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_RGB2GRAY)
    
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    #diff = cv2.subtract(grayA, grayB)
    diff = (diff * 255).astype("uint8")

    #thresh = cv2.threshold(diff, 180, 255, cv2.THRESH_OTSU)[1]
    #thresh = cv2.threshold(diff, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = cv2.adaptiveThreshold(diff, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 157, 77)

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    thresh[800:] = 255
    
    edge = cv2.Canny(thresh, 250, 300)
    ctrs, hier = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    plt.imshow(diff, cmap='gray')
    plt.show()

    plt.imshow(edge, cmap='gray')
    plt.show()
    
    #plt.imshow(edge, cmap='gray')
    #cv2.drawContours(edge, ctrs, -1, (0,255,0), 3)
    ctr = max(ctrs, key = len)
    #print(ctr)
    ctr_ind = (np.argmax([xy[0][1] for xy in ctr]))
    
    #print(ctr[ctr_ind])

    #diff = cv2.subtract(grayA, grayB)
    #diff = cv2.threshold(diff, 30, 150, cv2.THRESH_BINARY_INV)[1]
    return (ctr[ctr_ind])[0][0]



def angle_from_camera_to_dart(coordinates, board_width, fov=110):
    angle = [0, 0]
    angle[0] = coordinates[0] / board_width * fov
    angle[1] = coordinates[1] / board_width * fov
    return angle



if __name__ == "__main__":
    # set directory paths
    cur_dir = os.getcwd()
    parent_dir = os.path.dirname(cur_dir)
    print("current dir: ", cur_dir)
    print("parent dir: ", parent_dir)
    image_path = os.path.dirname(os.getcwd()) + "/images/test"
    print("image path: ", image_path)


    # initialize camera objects
    camX = cv2.VideoCapture(1) # First camera connected to USB port 0
    camY = cv2.VideoCapture(2) # Second camera connected to USB port 1

    # Capture images of dartboard with no dart
    input("\nPress enter to capture image of dartboard with no dart")
    capture_image(camX, "image_nodartX", image_path)
    capture_image(camY, "image_nodartY", image_path)

    # Capture images of dartboard with dart
    input("\nPress enter to capture image of dartboard with dart")
    capture_image(camX, "image_dartX", image_path)
    capture_image(camY, "image_dartY", image_path)


    # load recently captured images
    image_nodartX = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_nodartX.jpeg'))
    image_nodartY = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_nodartY.jpeg'))
    image_dartX = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_dartX.jpeg'))
    image_dartY = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_dartY.jpeg'))


    # display images and resolution
    images = [image_nodartX, image_nodartY, image_dartX, image_dartY]
    for image in images:
        plt.plot([image.shape[1]//2, image.shape[1]//2], [0, image.shape[0]], 'r-')
        plt.imshow(image)
        plt.show()
        print('Image Resolution: {} x {}'.format(image.shape[1], image.shape[0]))
    image_width = image.shape[1]


    # create diff images, canny images, and coordinates of dart
    x_coordinate = show_diff_image(image_dartX, image_nodartX)
    print("x-coordinate: " + str(x_coordinate))
    y_coordinate = show_diff_image(image_dartY, image_nodartY)
    print("x-coordinate: " + str(y_coordinate))
    darttip_pixel_coordinates = [x_coordinate, y_coordinate]


    # compute the angles from the camera to the dart using pixel width of board and camera field of view
    fov = 110
    angles_cameras_to_darts = angle_from_camera_to_dart(darttip_pixel_coordinates, image_width)
    print("coordinates:", darttip_pixel_coordinates)
    print("dart_angles:", angles_cameras_to_darts)

    
    # Calculate Coordinates of Dart Relative to Scoring Area
    cam_dist = 381 #mm
    x1, y1 = 381, 0 ## mm
    x2, y2 = 0, -381
    board_radius = 228.6 #mm

    # calculate angle relative to horizontal and vertical plane
    mod_angA, mod_angB = (fov/2 - angles_cameras_to_darts[0]) , (fov/2 - angles_cameras_to_darts[1]) + 90

    # convert to radians from degrees
    angA, angB  = mod_angA * math.pi/180, mod_angB * math.pi/180
    slopeA = math.tan(angA)
    slopeB = math.tan(angB)

    # use slope-intercept form to calculate x_dart and y_dart
    x_dart = (x1*slopeA - y1 -x2*slopeB + y2 )/(slopeA - slopeB)
    y_dart = (x_dart - x1) * slopeA
    print("x coordinate: " + str(x_dart))
    print("y coordinate: " + str(y_dart))


    # Create Visualiation of Dart Board
    fig, ax = plt.subplots() 
    ax.set_xlim(-cam_dist, cam_dist)
    ax.set_ylim(-cam_dist, cam_dist)

    dart_board = plt.Circle((0, 0), board_radius, edgecolor='black', fill=False)
    #dart_board = ax.pie([.05]*20)
    dart = plt.Arrow(x_dart, y_dart, 15, 15, color='black')
    bullseye = plt.Circle((0, 0), 10, edgecolor='black', fill=False)

    camA = plt.Rectangle((-cam_dist, -5), 1, 1, edgecolor='black', fill=False, clip_on=False)
    camB = plt.Rectangle((-5, -cam_dist), 1, 1, edgecolor='black', fill=False, clip_on=False) 

    ax.add_patch(dart_board)
    ax.add_patch(dart)
    ax.add_patch(bullseye)
    ax.add_patch(camA)
    ax.add_patch(camB)

    leg_Cam1_Dart = ax.axline((cam_dist, 0), slope= slopeA)
    leg_Cam2_Dart = ax.axline((0, -cam_dist), slope = slopeB)

    ax.plot(x_dart, y_dart)
    plt.show()



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
    if radius <= 5:
        score = 50
        print("Bullseye!!!")
    elif radius > 5 and radius <= 15:
        score = 25
        print("Bull!!!")
    elif radius >= 95 and radius <= 105:
        score = 3*slice_area
        print("Triple Score!!!")
    elif radius >= 160 and radius <=170:
        score = 2*slice_area
        print("Double Score!!!")
        
    elif radius > 170:
        score = 0
        print("Missed. Try Again.")
    else:
        score = slice_area
        print("Nice hit!!!")
    print("The score is: " + str(score))

