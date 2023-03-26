# script for testing functionality of cameras
import os
import cv2


def capture_image(camera, image_name, image_path):
    ret, img = camera.read() # Read an image from camera
    image_name = image_name + ".jpeg"
    cv2.imwrite(os.path.join(image_path, image_name), img)
    camera.release()
    print(image_name + " captured!")



# set directory paths
cur_dir = os.getcwd()
parent_dir = os.path.dirname(cur_dir)
print("current dir: ", cur_dir)
print("parent dir: ", parent_dir)
image_path = os.path.dirname(os.getcwd()) + "/images/test"
print("image path: ", image_path)

# initialize camera objects
camX = cv2.VideoCapture(0) # First camera connected to USB port 0
camY = cv2.VideoCapture(1) # Second camera connected to USB port 1

# Capture images of dartboard with no dart
input("\nPress enter to capture image of dartboard with no dart")
capture_image(camX, "image_nodartX", image_path)
capture_image(camY, "image_nodartY", image_path)

# Capture images of dartboard with dart
input("\nPress enter to capture image of dartboard with dart")
capture_image(camX, "image_dartX", image_path)
capture_image(camY, "image_dartY", image_path)
