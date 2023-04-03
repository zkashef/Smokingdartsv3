#temp
import cv2
import matplotlib.pyplot as plt
import os


# set directory paths
cur_dir = os.getcwd()
parent_dir = os.path.dirname(cur_dir)
image_path = cur_dir + "/images/test"
print("current dir: ", cur_dir)
print("parent dir: ", parent_dir)
print("image path: ", image_path)


# load recently captured images
image_nodartX = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_nodartX.jpeg'))
image_nodartY = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_nodartY.jpeg'))
image_dartX = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_dartX.jpeg'))
image_dartY = cv2.imread(os.path.join(parent_dir, 'images/test/', 'image_dartY.jpeg'))


# display images of darts
print("Image of dartx")
plt.plot([image_dartX.shape[1]//2, image_dartX.shape[1]//2], [0, image_dartX.shape[0]], 'r-')
# plot a horizontal line across the image
plt.plot([0, image_dartX.shape[1]], [image_dartX.shape[0]//2, image_dartX.shape[0]//2], 'r-')
plt.imshow(image_dartX)
plt.show()
    
print("Image of darty")
plt.plot([image_dartY.shape[1]//2, image_dartY.shape[1]//2], [0, image_dartY.shape[0]], 'r-')
plt.imshow(image_dartY)
plt.show()