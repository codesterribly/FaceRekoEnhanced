from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import RPi.GPIO as GPIO
import signal, time 
from gpiozero import Buzzer
import sys


#Declare Buzzer 
buz = Buzzer(26)

def buzz1sec():
	buz.on()
	time.sleep(0.5)
	buz.off()
	time.sleep(0.5)

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("\n\n")
	print("Received a new message: ")
	msgp = message.payload
	
	if msgp is None:
		buz.off()
	else: 
		print(message.payload)
		print("--------------\n\n")
		buzz1sec()
		buzz1sec()
		buzz1sec()
		buzz1sec()
		buzz1sec()
		
	

host = "a2ju1kllkt1ijl.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

try:
	my_rpi = AWSIoTMQTTClient("SoC")
	my_rpi.configureEndpoint(host, 8883)
	my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

	my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
	my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
	my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
	my_rpi.configureMQTTOperationTimeout(5)  # 5 sec
	
	my_rpi.connect()

	# Connect and subscribe to AWS IoT
	my_rpi.subscribe("FaceReko/failure", 1, customCallback)
	
except:
    print("Unexpected error:", sys.exc_info()[0])
	
while True: 
    try:   
        print("Waiting for messages to come in");
		#buz.off()
        sleep(5)
    except:
        print("Unexpected error")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
