# FaceRekoEnhanced
School IoT project. Simple Raspberry Pi face recognition security system for a door.
This project leverages Amazon's Rekognition service, AWS SNS service and was created for a Raspberry Pi with default account pi (adjust *install.sh* if different), a local mysql database and runs a simple WebApp.

The WebApp supports a login system with accounts in a MySQL DB. The FaceReko system can be turned ON or OFF from the WebApp along with viewing of access history with images.

Tapping of an RFID card triggers facial recognition with a buzzer giving audio cues and LEDs representing access allowed or denied.

When activated, the system beeps when a card is tapped. If the card is recognised, the camera will begin facial recognition with AWS Rekognition. If the person is recognised, a long beep is presented and the LEDs turns from Red to Green for 10 seconds, signifying access. Else the buzzer will sound 3 times if the person is not recognised and the red LED remains lit.

If the person was succesfully recognised, an email with the details of that login will be sent to a designated email address by AWS SNS push notification service.

## Hardware requirements:
- Raspberry Pi (Duh)
- PiCamera
- MFRC522 RFID reader and RFID card
- Red & Green LED diodes
- Buzzer

![Frizing diagram](https://github.com/yxkillz/FaceRekoEnhanced/blob/master/FaceReko%20Friz_v2.png)

## Things to note: 
1. Default Pi account is used in *install.sh*, change accordingly if needed.
2. MySQL login info in the codes has been hardcoded to my throwaway db, change/ setup accordingly.
3. There is a `collection` variable in *FaceReko.py* which needs to be changed to whatever collection name you set to later in install.

## Pre-requisite setups:
  
###  Amazon Web Service(AWS) Rekognition
  1) Create AWS account (Free Tier allows 5k API calls per month)
  2) Login and create a new IAM user with "AmazonRekognitionFullAccess" and "AdministratorAccess" permissions (Refer to AWS doc for help: https://docs.aws.amazon.com/rekognition/latest/dg/setting-up.html)
  3) Go to Security Credentials tab in IAM users page, generate and note down your aws_access_key_secret and aws_access_key_id

### Amazon Web Service(AWS) device registration
  1) Under AWS IoT core service register your raspberry pi as a thing (https://docs.aws.amazon.com/iot/latest/developerguide/register-device.html)
  2) Go to the details page of the newly registered thing and go to the "Interact" tab. Copy/ note down the Rest API Endpoint address.
  3) Next, go to the security tab of your thing and select "create certificate". Download all 4 generated certificates and rename them to remove the string of alpha numeric characters at the start of each file name. The final file names should be "certificate.pem.crt", "private.pem.key", "public.pem.key" and "rootca.pem". Place those files in the root FaceReko folder
  4) Click the activate button to activate the certificates.
  5) In the top right corner click "Attach a policy" then "Create new policy". Enter any name you want, enter "*" for Resource ARN* and check Allow under effect. Then complete the policy windows.
  6) In the main AWS IoT core nav bar select "Security Certificates" tab. Select the checkbox of the certificate you made earlier and select "attach policy" under Actions in the top right and attach the policy you just made. Then in the same Actions menu select "attach thing" and attach your raspberry pi thing. 
  
### AWS SNS
  1) Go to AWS SNS service. Then the topics tab under SNS and click "create new topic". Enter any name of your choice for Topic name and Display name.
  2) Note down the ARN address.
  3) Select the checkbox of the topic you just made and click "Edit topic policy" under Actions to allow everyone for both options.
  4) Under the same Action menu select "Subscribe to topic". For protocol select Email and enter your email address under Endpoint.
  5) An confirmation email will be sent to that email address. Click the link in the email to confirm the subscription.
  6) Return to the AWS IoT core service and select the Rules tab. Create a new rule, put any name you wish.
  7) Under Message Source section put "*" for Attribute*. For Topic Filter put "FaceReko/success" then click add action and select "Send a message as an SNS push notification"
  8) In the next page set the SNS target to the topic you made earlier, message format leave as raw.
  9) Click "Create a new role" and enter a role name you wish. Click Update Role then Add Action.
  10) Lastly, click Create rule to complete the process.

###  Local MySQL DB
  1) Install it, create accounts etc...(If needed) Import given sql file or follow steps 2 - 4 to create database and tables.
  2) Create a database called "FaceReko" 
  3) Create table "AccessLog" with the following columns and data types(Column Name, Data Type): 
		```
		(ID, int(5), AutoIncrement)
		(Name, varchar(50))
		(Time, datetime)
		(Similarity, decimal(10,2))
		(Confidence, decimal(10,2))
		(Image, varchar(30))
		```
  4) Create table "Login" with the following columns and data types (Column Name, Data Type): 
		```
		(Username, varchar(30))
		(Password, varchar(30))
		```
  
##  Install:
You can simply just copy *install.sh* to */home/pi/* and `sudo chmod +x install.sh` then run it with `sudo ./install.sh` to install all  pre-requisite packages, configure AWS and setup FaceReko files.
    
Mid-run of *install.sh* you will be prompted for AWS config info (This is where your AWS credentials you noted down earlier come in). For the first 2 prompts **enter your AWS Key ID then Access Key**. The 3rd option will be for an **AWS server region which supports the Rekognition service** (eg. "ap-northeast-1" which is tokyo). A full list of which servers support the service and their shorthands can be found at https://docs.aws.amazon.com/general/latest/gr/rande.html (ctrl-F "Rekognition"). 

For the last option **just hit enter and leave default**.

Once complete, there should be a folder named *FaceReko* in */home/pi/* and permissions for it setup. (If there are any permission issues with the program later on just manually `sudo` run the last couple `chmod & chown` commands in *install.sh*).

From here `cd` into the FaceReko folder.

### AWS Rekognition setup
Run `python add_collection.py -n 'home'` (Replace 'home' with whatever you want to call your collection, remember to change the `collection` variable accordingly in *FaceReko.py*)

Run `python take_selfie.py` to take a photo of you or the person you want recognised. It will be saved in the same folder as *selfie.jpg*.

Run `python add_image.py -i 'selfie.jpg' -c 'home' -l 'Name'` (Replace 'home' with your collection name from earlier and 'Name' with the name of the person in *selfie.jpg*.

### Additional AWS setup
In the root FaceReko folder run `aws iam create-role --role-name FaceReko --assume-role-policy-document file://iot-role-trust.json`

### Edit variables
In *FaceReko.py* and *server.py* change MySQL connection info if needed.

Run `python check_card.py` and tap your card on the reader to find out your card's UID. Edit *rfid.py*, look for the hid variable and change the numbers to your card's UID.

Lastly for this section, edit *FaceReko.py* and look for the `collection` variable. Change this to whatever you named your collection earlier.

## Usage:
Simply `cd` into the FaceReko folder and run `python server.py`

The webapp will be running on port 5000 (raspberryPi_IP:5000)

Once you enter the address into your browser URL bar, you will be presented with the login screen. Hit the Create Account button and create an account, regex is in place so only alpha numeric upto 30 characters are allowed. Place your RFID card on the reader before clicking submit. Once done proceed to login.

After login you are presented with the home screen. Below the welcome message is the control panel which displays the current status of the security system (Active or Offline) and controls to activate or deactivate the security system.

Below the control panel is the access log chart displays the history of people who were recognised by the facial recognition system. The chart shows name of the person recognised, time they gained access as well as similarity and confidence of that recognition and lastly there is the option to view the taken image of the person during that facial recognition request.

So to use the security system, simply activate it, scan your RFID card (buzzer beeps on card scan), face the camera. If recognised as an authorized person you will hear a long beep and the LEDs will change from red to green. Otherwise you will hear 3 beeps to signify access denied, unrecognised person.
