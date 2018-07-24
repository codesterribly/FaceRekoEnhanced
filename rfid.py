import RPi.GPIO as GPIO
import MFRC522
import signal, time
import FaceReko
from gpiozero import LED, Buzzer

uid = None
hid = [136, 4, 30, 198, 84]
prev_uid = None 
continue_reading = True
allow = False

#Declare LEDs and buzzer
ledRED = LED(21)
ledGREEN = LED(20)
buz = Buzzer(26)

#Set Red light
ledRED.on()

#Change Red to green for 10 seconds, buzz 2 seconds
def allowAccess():
	ledRED.off()
	ledGREEN.on()
	buz.on()
	time.sleep(2)
	buz.off()
	time.sleep(8)
	ledGREEN.off()
	ledRED.on()

#Causes buzzer to sound for 1 second
def buzz1sec():
	buz.on()
	time.sleep(0.5)
	buz.off()
	time.sleep(0.5)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
	global continue_reading
	print "Ctrl+C captured, ending read."
	continue_reading = False
	GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
mfrc522 = MFRC522.MFRC522()

# Welcome message
print "NFC Reader Active"
print "Press Ctrl-C to stop."

# This loop keeps checking for cards.
# Only the hardcoded reconsied card will trigger the code.

while continue_reading:
	
    #Scan for cards    
	(status,TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)

    #If a card is found
	if status == mfrc522.MI_OK:
		#Get the UID of the card
		(status,uid) = mfrc522.MFRC522_Anticoll()
		if uid==hid:
			prev_uid = uid
			buzz1sec()
			print("Card {} detected, Facial reko activated".format(uid))
			allow = FaceReko.main()
			if allow==True:
				allowAccess()
			else:
				buzz1sec()
				buzz1sec()
				buzz1sec()
				
	#Prevents continuous card scan spam. Waits 2 seconds before next scan
	time.sleep(2)
