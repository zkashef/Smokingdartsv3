# scoring.py
# script to tie everything together and determine score of thrown dart


# import scripts
from camera import *

# import libraries
import pyfirmata
import paho.mqtt.publish as publish
import atexit

def release_cameras():
    camX.cam.release()
    camY.cam.release()


if __name__ == "__main__":

    # release cameras when program exits
    atexit.register(release_cameras)

    # set directory paths
    cur_dir = os.getcwd()
    parent_dir = os.path.dirname(cur_dir)
    image_path = cur_dir + "/images/test"
    print("current dir: ", cur_dir)
    print("parent dir: ", parent_dir)
    print("image path: ", image_path)


    # initialize impact sensor on Arduino
    board = pyfirmata.Arduino('/dev/ttyACM0')
    KNOCK_SENSOR = "A0"
    THRESHOLD = .1
    sensor_reading = 0
    it = pyfirmata.util.Iterator(board)
    it.start()
    board.analog[0].mode = pyfirmata.INPUT


    # initialize MQTT server
    MQTT_SERVER = "broker.emqx.io"  # Address for the server that hosts the broker
    authentications = {'username': "kdyer", 'password': "Green82"}  # Username and password for sending the data

    # initialize cameras
    try:
        camX = Camera(0, image_path)
        camY = Camera(2, image_path)
    except:
        print("Gotta reboot or something to release those camera objects :/")
        exit()
    
    option = True
    while option: 

        # capture initial images
        camX.capture_image(image_path + "/image_nodartX")
        camY.capture_image(image_path + "/image_nodartY")
        
        
        ##### Wait for impact #####
        while True:
            sensor_reading = board.analog[0].read()
            #print(sensor_reading)
            if sensor_reading is not None:
                if sensor_reading >= THRESHOLD:
                    break
            time.sleep(0.1)


        # capture final images
        camX.capture_image(image_path + "/image_dartX")
        camY.capture_image(image_path + "/image_dartY")


        # get dart tip coordinates from images
        image_coordinates = camX.get_image_coordinates()
        print("image coordinates: ", image_coordinates)


        # calculate angles of dart to cameras
        angles_to_dart = camX.compute_angles(image_coordinates)
        print("angles to dart: ", angles_to_dart)


        # convert coordinates to be relative to dart board
        #cam_dist = 381 #mm
        x1, y1 = 445, 0
        x2, y2 = 0, 430
        board_radius = 228.6
        x_dart, y_dart = camX.get_board_coordinates(angles_to_dart, x1, y1, x2, y2)
        print("board coordinates: ", x_dart, y_dart)


        # calculate score of throw and send to app
        score, channel, slice_area = camX.get_score(x_dart, y_dart)
        publish.single(str(channel), str(slice_area), hostname=MQTT_SERVER, auth=authentications)


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
        ax.add_patch(dart_board)
        ax.add_patch(dart)
        ax.add_patch(bullseye)
        ax.add_patch(camA)
        ax.add_patch(camB)
        leg_Cam1_Dart = ax.axline((x1, y1), slope = camX.slope1)
        leg_Cam2_Dart = ax.axline((x2, y2), slope = camX.slope2)
        ax.plot(x_dart, y_dart)
        plt.show()

        option = input("1 to run program again, 0 to exit: ")

   