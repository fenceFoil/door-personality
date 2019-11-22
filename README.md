# Genuine People Personalities - Door Edition (GPPDE)

![Funny Logo](doc/gpp.png.jpg)

```plantuml
component Doorscript [
    **Door-watching script (gppdoor.py)**
    ---
    - Watches door sensor, triggers
    - When low on door quotes, fires up Quipgen in AWS
]

cloud Quipgen {
    interface FlaskAPI as api
    component "Quippy\n(GPT2)" as GPT2
    component "Filter\n(VADER)" as VADER
    component CorentinJ [
        Voice\n(Real-Time Voice Cloning\nby CorentinJ)
    ]
    api -> GPT2: generate quote
    GPT2 -> GPT2: Run dozens of times
    GPT2 --> VADER
    VADER -> VADER: Filter top several based on emotion
    VADER --> CorentinJ
    CorentinJ -> api: Pass back voiced quips
}

Doorscript <--> api

```

Doorscript maintains a folder, `~/DoorQuips/fresh/`, which must contain 10 fresh files to use. Files are moved to `~/DoorQuips/stale/` after being played.

To refresh quips, the Doorscript will launch a beefy EC2 instance with a GPU, prescripted to generate a batch of maybe 10 new quips. The server will offer one endpoint (`/quip_progress`), which announces the number of quips created so far, how many are left, and whether it is finished. As audio files are generated, they are placed in a folder. These will be zipped files, each containing:

* quip-[[UUID]].zip
  * metadata.json
  * quip.mp3

The `/quips/` downloads a zip of all the quip zips at once.

Meanwhile, Doorscript will poll `/quip_progress/` until quips are finished. Then it will download `/quips/` and ping `/server_dismissed/` to kill the server.

The server will remain alive for 3 minutes after it finishes generating quips as a safeguard, and will automatically shut down 15 minutes after first boot.

Doorscript will shuck all the quip.mp3 files out of the downloaded zip, renaming them with their UUID and placing them into `~/DoorQuips/fresh/`.

## Deployment

### On AWS:
* Created AWS user with all EC2 permissions (gppde)
  * Note the access key and the secret access key
* create keypair named `quipgenkey`
* create security group named `quipgen`
  * Open all ports to all traffic from everywhere. go wild.


### On Raspberry Pi:
(Note that on Raspain pis running python 3.5, there is a random number generator bug. One mitigation is:
```
sudo apt-get install rng-tools
```
)

Install requirements:

```bash
cd ~/door-personalities/doorscript/
sudo pip3 -r requirements.txt
# After this, only run the python scripts as sudo
```

Create a file using `nano /etc/boto.cfg`:

```
[Credentials]
aws_access_key_id=asdfasdfasdfasdfasdfasdf
aws_secret_access_key=asdfasdfasdfasdfasdfasdf
```

Wire a hall effect sensor as a pull down button onto pin 24 of your Raspberry Pi (doorscript.py sets pin number to watch), and secure the sensor to your door.

Attach speakers to your Raspberry Pi and test with some sounds.

Create AWS environment variables based on aws user `gppde`.

Make script run at startup automatically.

```bash
sudo nano /etc/rc.local
```

Add:

```bash
cd /home/pi/door-personality/doorscript
./rundoorscript.sh
```

Change `pi` to your user if it is not `pi`.

## Debugging features

* You can just launch the AWS server by running `python deployquipgen.py justlaunch`, which will not start the quipgen server in the background and will increase the length of the instance self destruct timer.