# import libraries
import cv2
import os
import time
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim
import matplotlib.pyplot as plt
import math


class Camera():
    def __init__(self, usb_index, path, fov=89, no_camera=False):
        self.image_path = path
        self.image_width = 0 # gets set in load_images()
        self.fov = fov # degrees
        self.no_camera = no_camera
        if no_camera:
            self.cam = None
            return
        
        # initialize camera objects and capture images of dartboard with no dart
        self.cam = cv2.VideoCapture(usb_index) # First camera connected to USB port usb_index
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cam.set(cv2.CAP_PROP_EXPOSURE, 50)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    

    # Determine Score of throw
    def get_score(self, x_dart, y_dart):
        radius = math.sqrt((x_dart**2)+(y_dart**2)) # find the radius

        # solve for the angle
        theta = math.atan(y_dart/x_dart) # in radians
        angle = theta * (180/math.pi) # convert to degrees

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
            channel = 11
            score = 50
            print("Bullseye!!!")
        elif radius > 5 and radius <= 15:
            channel = 11
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
            channel = 0
            score = slice_area
            print("Nice hit!!!")
        print("The score is: " + str(score))
        return score, channel, slice_area


    # Calculate Coordinates of Dart Relative to board
    def get_board_coordinates(self, angles_cameras_to_darts, x1, y1, x2, y2):
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
        
        total_angle1 = angle_to_center1 + (self.fov/2 - angles_cameras_to_darts[0]) 
        total_angle2 = angle_to_center2 + (self.fov/2 - angles_cameras_to_darts[1])
        
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
        self.slope1 = slope1
        self.slope2 = slope2
        return x_dart, y_dart

    # compute angles from camera to dart
    def compute_angles(self, coordinates, fov=89):
        angle = [0, 0]
        angle[0] = coordinates[0] / self.image_width * fov
        angle[1] = coordinates[1] / self.image_width * fov
        return angle
    
    
    # return both x and y coordinates of dart from image
    def get_image_coordinates(self):
        # load recently captured images
        image_nodartX, image_nodartY, image_dartX, image_dartY = self.load_images()
   
        # create diff images, canny images, and coordinates of dart
        right_x_coordinate, right_y_coordinate = self.get_image_coordinate(image_dartX, image_nodartX)
        print("right-side x-pixel_cor: " + str(right_x_coordinate))
        print("right-side y-pixel_cor: " + str(right_y_coordinate))
        right_xu = self.dist_calib(right_x_coordinate, right_y_coordinate)
        print("corrected right-side x_pixel: " + str(right_xu))

        top_x_coordinate, top_y_coordinate = self.get_image_coordinate(image_dartY, image_nodartY)
        print("top-side x-pixel_cor: " + str(top_x_coordinate))
        print("top-side y-pixel_cor: " + str(top_y_coordinate))
        top_xu = self.dist_calib(top_x_coordinate, top_y_coordinate)
        print("corrected top-side x_pixel: " + str(top_xu))
        coordinates = [right_xu, top_xu]
        return coordinates


    # capture image and save to image_path
    def capture_image(self, image_name):
        image_name += ".jpeg"
        self.cam.read()
        ret, img = self.cam.read() # Read an image from camera
        cv2.imwrite(os.path.join(self.image_path, image_name), img)
        print(image_name.split("/")[-1] + " captured!")
        return img

    # load all four images from the image_path
    def load_images(self):
        image_nodartX = cv2.imread(os.path.join(self.image_path, 'image_nodartX.jpeg'))
        image_nodartY = cv2.imread(os.path.join(self.image_path, 'image_nodartY.jpeg'))
        image_dartX = cv2.imread(os.path.join(self.image_path, 'image_dartX.jpeg'))
        image_dartY = cv2.imread(os.path.join(self.image_path, 'image_dartY.jpeg'))
        self.image_height, self.image_width, channels = image_nodartX.shape
        print('Image Resolution: {} x {}'.format(self.image_height, self.image_width))
        return image_nodartX, image_nodartY, image_dartX, image_dartY
    

    # create difference image, perform canny edge detection, and return coordinate of dart
    def get_image_coordinate(self, imageA, imageB):
        start_time = time.time()
        
        # crop top 1/5 of images
        imageA = imageA[int(self.image_height/5):self.image_height, 0:self.image_width]
        imageB = imageB[int(self.image_height/5):self.image_height, 0:self.image_width]

        # create difference image
        grayA = cv2.cvtColor(imageA, cv2.COLOR_RGB2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_RGB2GRAY)

        # plt.imshow(grayA, cmap='gray')
        # plt.show()
        # plt.imshow(grayB, cmap='gray')
        # plt.show()

        (score, diff) = compare_ssim(grayA, grayB, full=True)
        #diff = cv2.subtract(grayA, grayB)
        diff = (diff * 255).astype("uint8")

        
        thresh = cv2.threshold(diff, 200, 255, cv2.THRESH_OTSU)[1]#cv2.THRESH_OTSU)[1]
        
        # take care of the small noise through erosion and dilation, most lines will be taken away
        kernel = np.ones((9, 9), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel, iterations=1)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_ERODE, kernel, iterations=1)
    
        
        
        # perform canny edge detection
        edge = cv2.Canny(thresh, 250, 300)
        ctrs, hier = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # # display images
        # plt.imshow(diff, cmap='gray')
        # plt.show()
        # plt.imshow(thresh, cmap='gray')
        # plt.show()
        # plt.imshow(edge, cmap='gray')
        # plt.show()
        
        # find coordinates of dart tip in canny edge image

        #ctrs = [ctr for ctr in ctrs if min(ctr, key = lambda xy: xy[0][1]) > 500]
        """temp_ctrs = []

        for ctr in ctrs:
            min_y = min(ctr, key = lambda xy: xy[0][1])
            print(min_y)
            if min_y < 500:
                temp_ctrs+=[ctr]
        ctrs=temp_ctrs"""
            
        ctr = max(ctrs, key = lambda ctr: len(ctr) * cv2.minAreaRect(ctr)[1][1] *(500 - min(ctr, key = lambda xy: xy[0][1])[0][1]) )#(max(ctr, key=lambda x: x[0][1]) - min(ctr, key=lambda x: x[0][1])))
        ctr_ind = (np.argmax([xy[0][1] for xy in ctr]))

        y_pix = ctr[ctr_ind][0][1]

        ### in case multiple pixels have same y pixel coordinate
        x_tips = []
        for ctr_tup in ctr:
            if ctr_tup[0][1] == y_pix:
                x_tips+=[ctr_tup[0][0]]
        
        #print(sum(x_list)/len(x_list))
        x_pix = sum(x_tips)/len(x_tips)

        print("length of bottom line: " + str(len(x_tips)))
        
        print("Image processing time: " + str(time.time()-start_time))
        return (x_pix, y_pix)


    def dist_calib(self, x, y):
        coeffs = np.array([-1.16872310e-06,  5.39767230e-12, -6.77448104e-18, -8.43505986e-06, -1.01073783e-04])

       
        k1 = coeffs[0]
        k2 = coeffs[1]
        k3 = coeffs[2]
        p1 = coeffs[3]
        p2 = coeffs[4]

        k1_div = 1.86866052e-07
        x_diff = x - 960
        y_diff = y - 540
        r = math.sqrt(x_diff**2 + y_diff**2)

       
        xu = 0
        if x_diff < 430:

            xu = x + x_diff*r**2 * k1 + x_diff*r**4 * k2 + x_diff*r**6 * k3 + (r**2 + 2*(x_diff)**2) * p1 + 2*x_diff*y_diff*p2
            if (xu - x) > 100:
                xu =    960 + (x_diff)/(1 + r**2*k1_div)
        else:
            xu =    960 + (x_diff)/(1 + r**2*k1_div)

       
        return xu




