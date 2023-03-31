# script for testing functionality of cameras
import os
import cv2


def capture_image(camera, image_name, image_path):
    ret, img = camera.read() # Read an image from camera
    image_name = image_name + ".jpeg"
    cv2.imwrite(os.path.join(image_path, image_name), img)
    camera.release()
    print(image_name + " captured!")


# loop through possible camera indexes
#for i in range(10):
#    cap = cv2.VideoCapture(i)
#    # check if camera was opened successfully
#    if cap.read()[0]:
#        print(f"Camera index {i} is available")
#        cap.release()

# set directory paths
cur_dir = os.getcwd()
parent_dir = os.path.dirname(cur_dir)
print("current dir: ", cur_dir)
print("parent dir: ", parent_dir)
image_path = cur_dir + "/images/test"
print("image path: ", image_path)

# initialize camera objects
camX = cv2.VideoCapture(0) # First camera connected to USB port 0
print("camx works")
camY = cv2.VideoCapture(2) # Second camera connected to USB port 1
print("camy works")

# Capture images of dartboard with no dart
input("\nPress enter to capture image of dartboard with no dart")
capture_image(camX, "image_nodartX", image_path)
capture_image(camY, "image_nodartY", image_path)


# initialize camera objects
camX = cv2.VideoCapture(0) # First camera connected to USB port 0
print("camx works")
camY = cv2.VideoCapture(2) # Second camera connected to USB port 1
print("camy works")

# Capture images of dartboard with dart
input("\nPress enter to capture image of dartboard with dart")
capture_image(camX, "image_dartX", image_path)
capture_image(camY, "image_dartY", image_path)
