import sys
import boto3
import time
import requests
import datetime
import uuid
import random
import os
import shutil

import polly

## Usage:
## arg1: justlaunch
## OR
## arg1 is ip
## OR
## arg1 is ip, arg2 is noquips

######### CONFIGURATION #########

# AMI: Deep Learning AMI (Ubuntu 16.04) Version 26.0
BARE_DEEP_LEARNING_AMI = 'ami-07728e9e2742b0662'

# Choose an AMI here
LAUNCH_AMI = BARE_DEEP_LEARNING_AMI

#################################

startTime = datetime.datetime.now()

def isJustLaunchMode():
    return (len(sys.argv) > 1 and sys.argv[1] == 'justlaunch')

# If the server IP is passed on the command line, we won't start the AWS server again
quipgenServerIP = None
if len(sys.argv) <= 1 or isJustLaunchMode():
    ec2 = boto3.Session(region_name="us-west-2").resource('ec2')
    userData = open('awsuserdata.txt' if not isJustLaunchMode() else 'awsuserdata-justlaunch.txt', mode='r').read()
    
    instances = ec2.create_instances(ImageId=LAUNCH_AMI, InstanceType='g4dn.xlarge', MaxCount=1, MinCount=1, InstanceInitiatedShutdownBehavior='terminate', KeyName='quipgenkey', SecurityGroupIds=['quipgen'], UserData=userData)
    quipgenServerIP = None
    while quipgenServerIP == None:
        time.sleep(1)
        instances[0].reload()
        quipgenServerIP = instances[0].public_ip_address
    print ("Quipgen created:")
    print (quipgenServerIP)

    if not isJustLaunchMode():
        print ("Pinging until Quipgen starts responding...")
        response = None
        while response == None or response.status_code != 200:
            time.sleep(5)
            try:
                response = requests.get("http://"+quipgenServerIP+"/uptest", timeout=2)
            except requests.exceptions.Timeout:
                print ("Timeout...")
            except requests.exceptions.ConnectionError:
                print ("Connection refused...")

        print ("Quipgen responded! Time to launch: {} seconds".format((datetime.datetime.now()-startTime).seconds))
        print (quipgenServerIP)
else:
    quipgenServerIP = sys.argv[1]

if isJustLaunchMode():
    exit()


### Interacting with the Server: Generating Quips ###

def generateQuipText(serverIP):
    print ("Generating a quip...")
    prompt = "Good morning! How are you today?"
    response = None
    while response == None or response.status_code != 200:
        try:
            response = requests.post("http://"+serverIP+'/quip', json={"prompt":prompt})
            if response.status_code != 200:
                print ("SERVER ERROR {}".format(response.status_code))
                time.sleep(5)
        except requests.exceptions.ConnectionError:
            print ("Connection aborted, retrying")
            time.sleep(2)

    suffix = response.json()[0]
    return suffix #suffix.encode('ascii', 'ignore')

DATA_DIR = '/home/pi/door-personality/doorscript/'
UNSPOKEN_TEXT_DIR = DATA_DIR+'unspokenQuipTexts/'
SPOKEN_TEXT_DIR = DATA_DIR+'spokenQuipTexts/'
UNSPOKEN_QUIPS_DIR = DATA_DIR+'unspokenQuips/'
SPOKEN_QUIPS_DIR = DATA_DIR+'spokenQuips/'

for i in range (10):
    quipText = generateQuipText(quipgenServerIP)
    quipID = str(uuid.uuid4())
    with open(UNSPOKEN_TEXT_DIR+quipID, 'w+') as quipOut:
        quipOut.write(quipText)
    print ("Generated quip #{}".format(i+1))

### Convert text to quips

# Walk through all unspoken quips and speak them
for quipfile in os.listdir(UNSPOKEN_TEXT_DIR):
    with open (os.path.join(UNSPOKEN_TEXT_DIR, quipfile), 'r') as f:
        if polly.speak(text=f.read(), voice=random.choice(['Joanna', 'Salli']), outputPath=UNSPOKEN_QUIPS_DIR+quipfile+".ogg"):
            shutil.move(os.path.join(UNSPOKEN_TEXT_DIR, quipfile), os.path.join(SPOKEN_TEXT_DIR, quipfile))