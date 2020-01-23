import os
import random
from time import time, sleep
from gpiozero import Button
import pygame
import shutil

from notifications import sendNotification

sendNotification("Starting doorscript.py", priority=1)

DATA_DIR = '/home/pi/door-personality/doorscript/'
UNSPOKEN_TEXT_DIR = DATA_DIR+'unspokenQuipTexts/'
SPOKEN_TEXT_DIR = DATA_DIR+'spokenQuipTexts/'
UNSPOKEN_QUIPS_DIR = DATA_DIR+'unspokenQuips/'
SPOKEN_QUIPS_DIR = DATA_DIR+'spokenQuips/'

pygame.mixer.init()

def getQuipFiles():
    return [UNSPOKEN_QUIPS_DIR+f for f in os.listdir(UNSPOKEN_QUIPS_DIR) if f.endswith('.ogg')]

def speakRandomQuip():
    # Play a quip if possible
    if len(getQuipFiles()) > 0:
        # Choose quip and play the sound
        quipFile = random.choice(getQuipFiles())
        pygame.mixer.music.load(quipFile)
        pygame.mixer.music.play()

        # Send notification with original quote text
        quipID = quipFile[quipFile.rfind('/'):-4]
        with open(SPOKEN_TEXT_DIR+quipID, 'r') as f:
            sendNotification("Door Opened", f.read())

        # Move played quip to spoken folder
        shutil.move(quipFile, SPOKEN_QUIPS_DIR)

    # Generate more quips if needed
    remainingQuips = len(getQuipFiles())
    print ("Quips remaining: {}".format(remainingQuips))
    if remainingQuips < 5:
        print("Deploying quipgen...")
        sendNotification("Deploying QuipGen", "Creating AWS instance for ~$0.25 plus Polly due to low quips ({}) and logging into deployquipgen.log".format(remainingQuips), priority=5)
        os.system('python3 /home/pi/door-personality/doorscript/deployquipgen.py >> /home/pi/door-personality/doorscript/deployquipgen.log 2>&1')

speakRandomQuip()

# Respond to door opening and closing

def logMsg(msg):
    with open("/home/pi/doorlog.csv", "a") as myfile:
        myfile.write("{},{}\n".format(msg, int(time())))

door = Button(24)

logMsg('booted')

def onDoorClose():
    logMsg('closed')

def onDoorOpen():
    speakRandomQuip()
    logMsg('opened')
    

door.when_released = onDoorClose
door.when_pressed = onDoorOpen

while True:
    sleep(0.05)