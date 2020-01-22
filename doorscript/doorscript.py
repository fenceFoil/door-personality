import os
import random
from time import time, sleep
from gpiozero import Button
import pygame

DATA_DIR = '/home/pi/door-personality/doorscript/'
UNSPOKEN_TEXT_DIR = DATA_DIR+'unspokenQuipTexts/'
SPOKEN_TEXT_DIR = DATA_DIR+'spokenQuipTexts/'
UNSPOKEN_QUIPS_DIR = DATA_DIR+'unspokenQuips/'
SPOKEN_QUIPS_DIR = DATA_DIR+'spokenQuips/'

pygame.mixer.init()

def getQuipFiles():
    return [UNSPOKEN_QUIPS_DIR+f for f in os.listdir(UNSPOKEN_QUIPS_DIR) if f.endswith('.ogg')]

def speakRandomQuip():
    if len(getQuipFiles()) > 0:
        quipFile = random.choice(getQuipFiles())
        pygame.mixer.music.load(quipFile)
        pygame.mixer.music.play()
    #print ("Quotes remaining: {}".format(len(getQuoteFiles())))
    #if (len(getQuoteFiles())) < 5:
    #    print("Deploying quipgen...")
    #    os.system('python3 deployquipgen.py >> doorscript.log 2>&1')

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