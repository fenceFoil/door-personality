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
* create keypair named `quipgenkey`
* create security group named `quipgen`
  * Open all ports to all traffic from everywhere. go wild.


### On Raspberry Pi:
Create AWS environment variables based on aws user `gppde`.

Make script run at startup automatically.

```bash
sudo nano /etc/rc.local
```

Add
```bash
export AWS_ACCESS_KEY_ID=asdfasdfasdfasdfasdfasdf
export AWS_SECRET_ACCESS_KEY=asdfasdfasdfasdfasdfsadf
cd /home/pi/door-personality/doorscript
python3 -u doorscript.py >> /home/pi/door/personality/doorscript/doorscript.log 2>&1 &
```

## Quipgen


...

terminate quipgen instance