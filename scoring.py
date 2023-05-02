# scoring.py
# script to tie everything together and determine score of thrown dart


# import scripts
from camera import *

# import libraries
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import atexit
import serial
import time
import os

def release_cameras(camX, camY):
    try:
        camX.cam.release()
        camY.cam.release()
        print("Cameras released")
    except:
        print("Cameras unable to be released")
    return

def initalize_cameras(image_path):
    # initialize cameras
    try:
        camY = Camera(0, image_path)
        camX = Camera(2, image_path)
        # release cameras when program exits
        atexit.register(release_cameras, camX, camY)
        return  camX, camY
    except:
        print("Gotta reboot or something to release those camera objects :/")
        exit()

def display_image(img):
    image_height, image_width, channels = img.shape
    plt.imshow(img)
    plt.plot([int(image_width/2), int(image_width/2)], [0, image_height], 'r-')
    plt.show()
    return

# Create Visualiation of Dart Board in Matplotlib
def visualize_board(x_dart, y_dart, x1, y1, x2, y2, board_radius):
    fig, ax = plt.subplots() 
    ax.set_xlim(-400, 400)
    ax.set_ylim(-400, 400)
    dart_board = plt.Circle((0, 0), board_radius, edgecolor='black', fill=False)
    #dart_board = ax.pie([.05]*20)
    dart = plt.Arrow(x_dart, y_dart, 15, 15, color='black')
    bullseye = plt.Circle((0, 0), 5, edgecolor='black', fill=False)
    bulls = plt.Circle((0, 0), 15, edgecolor='black', fill=False)
    inner = plt.Circle((0, 0), 95, edgecolor='black', fill=False)
    inner_outer = plt.Circle((0, 0), 105, edgecolor='black', fill=False)
    outer_inner = plt.Circle((0, 0), 160, edgecolor='black', fill=False)
    outer = plt.Circle((0, 0), 170, edgecolor='black', fill=False)
    camA = plt.Rectangle((x1, y1), 10, 10, edgecolor='black', fill=False, clip_on=False)
    camB = plt.Rectangle((x2, y2), 10, 10, edgecolor='black', fill=False, clip_on=False)

    ax.add_patch(inner)
    ax.add_patch(inner_outer)
    ax.add_patch(outer_inner)
    ax.add_patch(outer)
    ax.add_patch(bulls) 
    ax.add_patch(dart_board)
    ax.add_patch(dart)
    ax.add_patch(bullseye)
    ax.add_patch(camA)
    ax.add_patch(camB)
    leg_Cam1_Dart = ax.axline((x1, y1), slope = camX.slope1)
    leg_Cam2_Dart = ax.axline((x2, y2), slope = camX.slope2)
    ax.plot(x_dart, y_dart)
    plt.show()
    return
    

if __name__ == "__main__":
    try:
        # set directory paths
        cur_dir = os.getcwd()
        parent_dir = os.path.dirname(cur_dir)
        image_path = cur_dir + "/images/test"
        print("current dir: ", cur_dir)
        print("parent dir: ", parent_dir)
        print("image path: ", image_path)


        # initialize impact sensor on Arduino
        devtty = ''
        path = "/dev"

        # Check if the directory path /dev contains ttyACM0 or ttyACM1
        if any(fname == "ttyACM0" for fname in os.listdir(path)):
            devtty = '/dev/ttyACM0'
        elif any(fname == "ttyACM1" for fname in os.listdir(path)):
            devtty = '/dev/ttyACM1'
        else:
            print("Neither ttyACM0 nor ttyACM1 was found in the path /dev.")
        ser = serial.Serial(devtty, 9600)
        

        # initialize MQTT server
        MQTT_SERVER = "broker.emqx.io"  # Address for the server that hosts the broker
        authentications = {'username': "kdyer", 'password': "Green82"}  # Username and password for sending the data
        
        # wait for message before entering loop
        msg = subscribe.simple("Start", hostname=MQTT_SERVER, auth=authentications)
        print(msg.payload)

        throw_count = 1
        option = 1
        while option:
            # wait for message if 3 throws
            if throw_count == 3:
                msg = subscribe.simple("Start", hostname=MQTT_SERVER, auth=authentications)
                print(msg.payload)
                throw_count = 1

            # capture time it takes to capture images and send score
            start_time = time.time()
            camX, camY = initalize_cameras(image_path)
            
            #time.sleep(3)
            # capture initial images
            img = camX.capture_image(image_path + "/image_nodartX")
            #display_image(img)
            img = camY.capture_image(image_path + "/image_nodartY")
            #display_image(img)


            ##### Wait for impact #####
            print("Waiting for impact...")
            
            while True:
                ser.reset_input_buffer()
                data = ser.readline().decode('utf-8').strip()  # Read and decode data from the serial port
                print("Received data:", data)  # Print the received data
                if int(data) == 1:
                    time.sleep(1)
                    break
        
            # capture final images
            img = camX.capture_image(image_path + "/image_dartX")
            display_image(img)
            img = camY.capture_image(image_path + "/image_dartY")
            display_image(img)
            
            release_cameras(camX, camY)

            # get dart tip coordinates from images
            image_coordinates = camX.get_image_coordinates()
            print("image coordinates: ", image_coordinates)


            # calculate angles of dart to cameras
            angles_to_dart = camX.compute_angles(image_coordinates)
            print("angles to dart: ", angles_to_dart)


            # convert coordinates to be relative to dart board
            #cam_dist = 381 #mm
            x1, y1 = 294, 0
            x2, y2 = 0, 295
            board_radius = 228.6
            x_dart, y_dart = camX.get_board_coordinates(angles_to_dart, x1, y1, x2, y2)
            print("board coordinates: ", x_dart, y_dart)


            # calculate score of throw and send to app
            score, channel, slice_area = camX.get_score(x_dart, y_dart)
            if score == 25:
                ser.write(str(25).encode('utf-8'))
                publish.single(str(channel), str(25), hostname=MQTT_SERVER, auth=authentications)
            elif score == 50:
                ser.write(str(50).encode('utf-8'))
                publish.single(str(channel), str(50), hostname=MQTT_SERVER, auth=authentications)
            else:
                ser.write(str(slice_area).encode('utf-8'))
                publish.single(str(channel), str(slice_area), hostname=MQTT_SERVER, auth=authentications)
            print("Score: ", score)
            print("Channel: ", channel)
            print("Slice Area: ", slice_area)

            end_time = time.time()
            print("Time to capture images & capture images: ", end_time - start_time)
            
            # visualize board
            visualize_board(x_dart, y_dart, x1, y1, x2, y2, board_radius)
        
            throw_count += 1
            option = int(input("1 to run program again, 0 to exit: "))

        release_cameras(camX, camY)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        release_cameras(camX, camY)
        exit()


   