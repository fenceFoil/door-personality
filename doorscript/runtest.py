import os
import random
from time import time, sleep
from gpiozero import Button

def getQuoteFiles():
    return [f for f in os.listdir(dir) if f.endswith('.txt')]

def speakRandomQuote():
    quoteFile = random.choice(getQuoteFiles())
    os.system('cat ~/door-personality/queuedQuotes/{} | espeak --stdin -a30 -g1 -p30 -m'.format(quoteFile))
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