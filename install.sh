#!/bin/bash

echo 'Updating and installing dependencies...'
apt-get update && apt-get -y upgrade

apt-get install -y build-essential python-setuptools python-pip awscli

pip install boto3 watchdog simplejson PiCamera
rm -rf ~/.cache/pip

echo 'Configuring AWS...'
aws configure

cd /home/pi

echo 'Retreving repo files...'
git clone https://github.com/yxkillz/FaceReko.git

echo 'Adjusting permissions and creating folders'
chown pi:pi FaceReko
mkdir FaceReko/static
mkdir FaceReko/static/images
chmod 777 FaceReko/static/images

echo 'Done!'

exit 0

