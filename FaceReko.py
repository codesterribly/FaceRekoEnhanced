#!/usr/bin/env python

from picamera import PiCamera
import time
import os, MySQLdb
import boto3 as b3
from argparse import ArgumentParser
from time import gmtime, strftime, sleep
from gpiozero import LED
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = "a2ju1kllkt1ijl.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

my_rpi = AWSIoTMQTTClient("FaceReko")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

#my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
#my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
#my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
#my_rpi.configureMQTTOperationTimeout(5)  # 5 sec
my_rpi.connect()

def get_client():
    return b3.client('rekognition')
	
def check_face(client, file):
    face_detected = False
    with open(file, 'rb') as image:
        response = client.detect_faces(Image={'Bytes': image.read()})
        if (not response['FaceDetails']):
            face_detected = False
        else: 
            face_detected = True

    return face_detected, response

def check_matches(client, file):
    collection = 'home'
    face_matches = False
    with open(file, 'rb') as image:
        response = client.search_faces_by_image(CollectionId=collection, Image={'Bytes': image.read()}, MaxFaces=1, FaceMatchThreshold=85)
        if (not response['FaceMatches']):
            face_matches = False
        else:
            face_matches = True

    return face_matches, response

count = 2
camera = PiCamera()

def main():
	try:
		db = MySQLdb.connect("localhost", "root", "dmitiot", "FaceReko")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL database")
	
	directory = 'static/images'

	#if not os.path.exists(directory):
	#	os.makedirs(directory)

	print 'A photo will be taken in 2 seconds...'

	for i in range(count):
		print (count - i)
		time.sleep(1)

	milli = int(round(time.time() * 1000))
	img_save= 'image_{0}.jpg'.format(milli)
	image = '{0}/{1}'.format(directory, img_save)
	#img_save = image.replace('.jpg', '')
	camera.capture(image)
	print 'Your image was saved to %s' % image
	
	client = get_client()
    
	print 'Running face checks against image...'
	result, resp = check_face(client, image)

	if (result):
		print 'Face(s) detected with %r confidence...' % (round(resp['FaceDetails'][0]['Confidence'], 2))
		print 'Checking for a face match...'
		resu, res = check_matches(client, image)
    
		if (resu):
			person = res['FaceMatches'][0]['Face']['ExternalImageId']
			similarity = round(res['FaceMatches'][0]['Similarity'], 2)
			confidence = round(res['FaceMatches'][0]['Face']['Confidence'], 2)
			final = 'Identity matched %s with %r similarity and %r confidence...' % (person, similarity, confidence)
			print(final)
			my_rpi.publish("FaceReko/success", final, 1)			

			sql = "INSERT into AccessLog (Name, Time, Similarity, Confidence, Image) VALUES (%s, NOW(), %s, %s, %s)"
			#print(sql)
			curs.execute(sql, (person, similarity, confidence, img_save))
			db.commit()
			curs.close()
			db.close()
			
			return True
			
		else:
			print 'No face matches detected...'
			msg = "Unauthorized access attempt!"
			my_rpi.publish("FaceReko/failure", msg, 1)
			

	else :
		print "No faces detected..."
		msg = "Unauthorized access attempt!"
		my_rpi.publish("FaceReko/failure", msg, 1)
 
        
if __name__ == '__main__':
    main()