# import libraries
import cv2
import os

class Camera():
    def __init__(self, usb_index, path):
        # initialize camera objects and capture images of dartboard with no dart
        self.cam = cv2.VideoCapture(usb_index) # First camera connected to USB port usb_index
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cam.set(cv2.CAP_PROP_EXPOSURE, 50)

        self.image_path = path
        


    def capture_image(image_name):
        ret, img = camera.read() # Read an image from camera
        #cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)
        image_path = image_name + ".jpeg"
        cv2.imwrite(os.path.join(self.image_path, image_name), img)
        camera.release()
        print(image_name + " captured!")