import os
import random

def getQuoteFiles():
    return [f for f in os.listdir(dir) if f.endswith('.txt')]

quoteFile = random.choice(getQuoteFiles())
os.system('cat ~/door-personality/queuedQuotes/{} | espeak --stdin -a30 -g1 -p30 -m'.format(quoteFile))
os.remove(quoteFile)
print ("Quotes remaining: {}".format(len(getQuoteFiles())))