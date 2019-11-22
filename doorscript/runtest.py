import os
import random
from time import time, sleep
from gpiozero import Button

QUEUE_DIR = '/home/pi/door-personality/doorscript/queuedQuotes/'

def getQuoteFiles():
    return [QUEUE_DIR+f for f in os.listdir(QUEUE_DIR) if f.endswith('.txt')]

def speakRandomQuote():
    quoteFile = random.choice(getQuoteFiles())
    os.system('cat {} | espeak --stdin -a30 -s120 -p110 -ven+m6 -m'.format(quoteFile))
    os.remove(quoteFile)
    print ("Quotes remaining: {}".format(len(getQuoteFiles())))

speakRandomQuote()

# Respond to door opening and closing

def logMsg(msg):
    with open("/home/pi/doorlog.csv", "a") as myfile:
        myfile.write("{},{}\n".format(msg, int(time())))

door = Button(24)

logMsg('booted')

def onDoorClose():
    logMsg('closed')

def onDoorOpen():
    speakRandomQuote()
    logMsg('opened')
    

door.when_released = onDoorClose
door.when_pressed = onDoorOpen

while True:
    sleep(0.05)