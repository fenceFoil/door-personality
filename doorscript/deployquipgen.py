import boto3
import time
import requests
import datetime

startTime = datetime.datetime.now()

ec2 = boto3.resource('ec2')
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
