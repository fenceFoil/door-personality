import sys
import boto3
import time
import requests
import datetime
import uuid
import random

startTime = datetime.datetime.now()

# If the server IP is passed on the command line, we won't start the AWS server again
quipgenServerIP = None
if len(sys.argv) <= 1:
    ec2 = boto3.Session(region_name="us-west-2").resource('ec2')
    userData = open('awsuserdata.txt',mode='r').read()
    instances = ec2.create_instances(ImageId='ami-04121e1f9d541d468', InstanceType='g4dn.xlarge', MaxCount=1, MinCount=1, InstanceInitiatedShutdownBehavior='terminate', KeyName='quipgenkey', SecurityGroupIds=['quipgen'], UserData=userData)
    quipgenServerIP = None
    while quipgenServerIP == None:
        time.sleep(1)
        instances[0].reload()
        quipgenServerIP = instances[0].public_ip_address
    print ("Quipgen created:")
    print (quipgenServerIP)

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

def generateSuffixForPrompt(serverIP, prompt):
    response = requests.post("http://"+serverIP+'/gpt2', json={"prompt":prompt})
    if response.status_code != 200:
        print("SERVER ERROR {}".format(response.status_code))
        return "SERVER ERROR {}".format(response.status_code)
    else:
        # TODO: Process GPT2
        suffix = response.text
        accepted = ""
        #suffix = suffix.replace ('"', "")
        #suffix = suffix.replace ("'", "" )
        suffix = suffix.replace ("\n", " ")
        suffix = suffix.replace ("\r", " ")
        suffix = suffix.replace ('..', ". ")
        suffix = suffix.replace ('...', ". ")
        suffix = suffix.replace ('.....', ". ")
        # Put a space before end of text marker to make sure it's its own word
        suffix = suffix.replace ('<|endoftext|>', ' <|endoftext|> ')
        # Remove all quotation marks: not needed in either reviews or convincing pickup lines
        suffix = suffix.replace ('"', '')
        suffix = suffix.replace ('“', '')
        suffix = suffix.replace ('”', '')

        notFirstLoop = False
        thisSentenceEnds = False
        for token in suffix.split(" "):
            notFirstLoop = True
            #print (token)
            accepted += (" " if notFirstLoop else "") + token
            killloop = False
            for endchar in [".", "!", ":", "?", "<|endoftext|>"]:
                if endchar in token:
                    killloop = True
                    thisSentenceEnds = True
            if killloop:
                #print ('breaking')
                break
        if not thisSentenceEnds:
            accepted = accepted[:150]+"..."
        accepted = accepted.replace("<|endoftext|>", "")

        return accepted #accepted.encode('ascii', 'ignore')




QUEUE_DIR = '/home/pi/door-personality/doorscript/queuedQuotes/'

for i in range (10):
    quoteText = generateSuffixForPrompt(quipgenServerIP, "Good morning! How are you today?")
    with open(QUEUE_DIR+'quote'+str(uuid.uuid4())+'.txt', 'w+') as quoteOut:
        quoteOut.write(quoteText)
    print ("Generated quote #{}".format(i+1))