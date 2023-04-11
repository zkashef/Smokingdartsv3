# import libraries
import cv2
import matplotlib.pyplot as plt
import os
from skimage.metrics import structural_similarity as compare_ssim
import numpy as np
import math
import time
import pyfirmata
import paho.mqtt.publish as publish

MQTT_SERVER = "broker.emqx.io"  # Address for the server that hosts the broker
#MQTT_SERVER = "broker.hivemq.com"
authentications = {'username': "kdyer", 'password': "Green82"}  # Username and password for sending the data


def capture_image(camera, image_name, path):
    ret, img = camera.read() # Read an image from camera
    #cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)
    image_name = image_name + ".jpeg"
    cv2.imwrite(os.path.join(path, image_name),  img)
    camera.release()
    print(image_name + " captured!")

def distort_calib(img):
    dist = np.loadtxt('dist_matrix.txt', dtype= float)
    mtx = np.loadtxt('cam_matrix.txt', dtype=float )
    
    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
    # crop the image
    x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]
    
    return dst

def show_diff_image(imageA, imageB):
    
    start_time = time.time()
    
    grayA = cv2.cvtColor(imageA, cv2.COLOR_RGB2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_RGB2GRAY)
    
    #grayA = distort_calib(grayA)
    #grayB = distort_calib(grayB)
    
    
    (score, diff) = compare_ssim(grayA, grayB, gradient_method = 'gaussian', full=True)
    
    diff = (diff * 255).astype("uint8")

    
    thresh = cv2.adaptiveThreshold(diff, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 185, 75)

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    
    thresh[:40] = 255
    
    edge = cv2.Canny(thresh, 100, 250)
    ctrs, hier = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #plt.imshow(diff, cmap='gray')
    #plt.show()

    plt.imshow(edge, cmap='gray')
    plt.show()
    
    #plt.imshow(edge, cmap='gray')
    
    ctr = max(ctrs, key = len)
    
    ctr_ind = (np.argmax([xy[0][1] for xy in ctr]))
    
    

    
    
    
    end_time = time.time()
    
    print("Image processing time: " + str(end_time-start_time))
    return (ctr[ctr_ind])[0][0]



def angle_from_camera_to_dart(coordinates, board_width, foc_len, fov=110):
    angle = [0, 0]
    angle[0] = coordinates[0] / board_width * fov
    angle[1] = coordinates[1] / board_width * fov
    #angle[0] = fov/2 + math.atan((coordinates[0]-board_width/2)/foc_len)*180/math.pi
    #angle[1] = fov/2 + math.atan((coordinates[1]-board_width/2)/foc_len)*180/math.pi
    return angle



if __name__ == "__main__":
    # set directory paths
    
    while True: 
        
        input("Enter start: ")
        
        cur_dir = os.getcwd()
        parent_dir = os.path.dirname(cur_dir)
        image_path = cur_dir + "/images/test"
        print("current dir: ", cur_dir)
        print("parent dir: ", parent_dir)
        print("image path: ", image_path)
    
    
        #### Impact sensor setup ####
        
        board_flag=False
        dir_path = "/dev/"
        files = os.listdir(dir_path)
        files = [f for f in files if f.startswith('/dev/ttyACM')]
        board = pyfirmata.Arduino('/dev/ttyACM0')
        for file in files:
            if file.endswith('0'):
                board = pyfirmata.Arduino('/dev/ttyACM0')
                board_flag = True
            elif file.endwith('1'):
                board = pyfirmata.Arduino('/dev/ttyACM1')
                board_flag = True
        if board_flag == False:
            print("impact sensor not detected")
            
        KNOCK_SENSOR = "A0"
        THRESHOLD = .1
        sensor_reading = 0
        
        it = pyfirmata.util.Iterator(board)
        it.start()
        board.analog[0].mode = pyfirmata.INPUT
        

        # initialize camera objects and capture images of dartboard with no dart
        camX = cv2.VideoCapture(0) # First camera connected to USB port 0
        camY = cv2.VideoCapture(2) # Second camera connected to USB port 1
        
        camX.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camX.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        camY.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camY.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        camX.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        camY.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        camX.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        camY.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        camX.set(cv2.CAP_PROP_EXPOSURE, 50)
        camY.set(cv2.CAP_PROP_EXPOSURE, 50)
        
        capture_image(camX, "image_nodartX", image_path)
        capture_image(camY, "image_nodartY", image_path)
        
        
        ##### While loop that waits for impact #####
        #input("\nPress enter to capture image of dartboard with dart")
        while True:
            sensor_reading = board.analog[0].read()
            #print(sensor_reading)
            if sensor_reading is not None:
                if sensor_reading >= THRESHOLD:
                    break
            

        
        #  Reinitialize camera objectsCapture images of dartboard with dart
        camX = cv2.VideoCapture(0) # First camera connected to USB port 0
        camY = cv2.VideoCapture(2) # Second camera connected to USB port 1
        
        
        camX.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camX.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        camY.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camY.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        camX.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        camY.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        camX.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        camY.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        camX.set(cv2.CAP_PROP_EXPOSURE, 60)
        camY.set(cv2.CAP_PROP_EXPOSURE, 60)
        
        capture_image(camX, "image_dartX", image_path)
        capture_image(camY, "image_dartY", image_path)
        


        # load recently captured images
        image_nodartX = cv2.imread(os.path.join(image_path, 'image_nodartX.jpeg'))
        image_nodartY = cv2.imread(os.path.join(image_path, 'image_nodartY.jpeg'))
        image_dartX = cv2.imread(os.path.join(image_path, 'image_dartX.jpeg'))
        image_dartY = cv2.imread(os.path.join(image_path, 'image_dartY.jpeg'))


        # display images and resolution
        images = [image_nodartX, image_nodartY, image_dartX, image_dartY]
        for image in images:
            #plt.plot([image.shape[1]//2, image.shape[1]//2], [0, image.shape[0]], 'r-')
            #plt.imshow(image)
            #plt.show()
            print('Image Resolution: {} x {}'.format(image.shape[1], image.shape[0]))
        image_height, image_width, channels = image_nodartX.shape
        print("image_width" + str(image_width))

        # create diff images, canny images, and coordinates of dart
        x_coordinate = show_diff_image(image_dartX, image_nodartX)
        print("x-pixel_cor: " + str(x_coordinate))
        y_coordinate = show_diff_image(image_dartY, image_nodartY)
        print("x-pixel_cor: " + str(y_coordinate))
        darttip_pixel_coordinates = [x_coordinate, y_coordinate]


        # compute the angles from the camera to the dart using pixel width of board and camera field of view
        fov = 110 
        foc_len = (image_width/2)/math.tan((fov/2)*math.pi/180)
        angles_cameras_to_darts = angle_from_camera_to_dart(darttip_pixel_coordinates, image_width, foc_len, fov)
        print("coordinates:", darttip_pixel_coordinates)
        print("dart_angles:", angles_cameras_to_darts)
        print("image_width: ", image_width)


        
        
        # Calculate Coordinates of Dart Relative to Scoring Area
        #cam_dist = 381 #mm
        x1, y1 = 307, -8
        x2, y2 = 0, 303
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
        
        
        publish.single(str(channel), str(slice_area), hostname=MQTT_SERVER, auth=authentications)
        plt.show()
