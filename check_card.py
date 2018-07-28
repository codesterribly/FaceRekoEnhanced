import RPi.GPIO as GPIO
import MFRC522
import signal, sys

uid = None
prev_uid = None 
continue_reading = True

# Create an object of the class MFRC522
mfrc522 = MFRC522.MFRC522()

# This loop keeps checking for chips.
# If one is near it will get the UID
def read():
	print("Waiting for card")
	while continue_reading:
	    
	    # Scan for cards    
	    (status,TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)
	
	    # If a card is found
	    if status == mfrc522.MI_OK:
	        # Get the UID of the card
	        (status,id) = mfrc522.MFRC522_Anticoll()
		uid = ''.join(str(i) for i in id )
	        print("UID of card is {}".format(uid))
		return uid
		GPIO.cleanup()
		sys.exit()