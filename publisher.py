import paho.mqtt.publish as publish

MQTT_SERVER = "broker.emqx.io"
#MQTT_SERVER = "broker.hivemq.com"
MQTT_PATH = "1"
authentications = {'username': "kdyer", 'password': "Green"}

# A function to publish the data to the MQTT server
# this fnciton asks the user what channel they want, ranging from 0 to 3
# the function asks the user what score they want to throw, ranging from 0 to 50
# the function then publishes the data to the MQTT server
shouldContinue = True
while shouldContinue:
    channel = input("Miss, single, double, or triple? (0-3): ")
    if channel == "q":
        break
    score = input("Enter score (0-50): ")
    if score == "q":
        break
    publish.single(channel, score, hostname=MQTT_SERVER, auth=authentications)
    #shouldContinue = input("Continue? (y/n): ")
    #if shouldContinue == "n":
     #   shouldContinue = False

# publish.single(MQTT_PATH, "30", hostname=MQTT_SERVER, auth={'username':"kdyer",'password':"Green"})
