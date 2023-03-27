#!/usr/bin/env python3
import pyfirmata
import time
if __name__ == '__main__':
    board = pyfirmata.Arduino('/dev/ttyACM0')
    print("Communication Successfully started")
    
    
    KNOCK_SENSOR = "A0"
    THRESHOLD = .1
    
    sensor_reading = 0
    
    #knock_sensor = board.get_pin(KNOCK_SENSOR)
    
    it = pyfirmata.util.Iterator(board)
    it.start()
    #serial = board.get_pin('tx').serial
    
    board.analog[0].mode = pyfirmata.INPUT
    
    while True:
        sensor_reading = board.analog[0].read()
        #print(sensor_reading)
        if sensor_reading is not None:
            if sensor_reading >= THRESHOLD:
                print("Knock")
        time.sleep(0.1)
        
