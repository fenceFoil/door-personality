# I am using Gotify to notify my phone of calls out to AWS and door events.

import requests

gotifyaddress = None
gotifyappkey = None

with open ('gotifyaddress.txt', 'r') as f:
    gotifyaddress = f.read()
with open ('gotifyappkey.txt', 'r') as f:
    gotifyappkey = f.read()

# body may be none defaults to same as title
def sendNotification(title, body=None, priority=5):
    global gotifyaddress
    global gotifyappkey

    if body == None:
        body = title
    
    try:
        response = requests.post(gotifyaddress+'message', params={"token":gotifyappkey}, json={'message':body, 'title':title, 'priority':priority})
        if response.status_code != 200:
            print ("notifications.sendNotification(): server error {}".format(response.status_code))
    except requests.exceptions.ConnectionError:
        print ("notifications.sendNotification(): connection error. not retrying.")