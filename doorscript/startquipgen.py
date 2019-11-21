import boto3
import time

ec2 = boto3.resource('ec2')
userData = open('awsuserdata.txt',mode='r').read()
instances = ec2.create_instances(ImageId='ami-04121e1f9d541d468', InstanceType='g4dn.xlarge', MaxCount=1, MinCount=1, InstanceInitiatedShutdownBehavior='terminate', KeyName='quipgenkey', SecurityGroupIds=['quipgen'], UserData=userData)
time.sleep(5)
instances[0].reload()
print(instances[0].public_ip_address)
