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

***

Note: Must upload 2x model files from pi to quipgen server and a trigger file when completed

## Quipgen detailed design notes (TEMP)

* generateSentences()

## Deployment

### On AWS:
* Created AWS user with all EC2 permissions (`gppde`)
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

Create a file using `nano /etc/boto.cfg` and the credentials for your aws user `gppde`:

```
[Credentials]
aws_access_key_id=asdfasdfasdfasdfasdfasdf
aws_secret_access_key=asdfasdfasdfasdfasdfasdf
```

Wire a hall effect sensor as a pull down button onto pin 24 of your Raspberry Pi (doorscript.py sets pin number to watch), and secure the sensor to your door.

Attach speakers to your Raspberry Pi and test with some sounds.

Make script run at startup automatically:

```bash
sudo nano /etc/rc.local
```

Add:

```bash
cd /home/pi/door-personality/doorscript
./rundoorscript.sh
```

Change `pi` to your user if it is not `pi`.

Copy over the quipgenkey.pem private key file you created earlier, and upload it to ~/door-personalities/quipgen/
Then run:

```bash
chmod 600 ../quipgen/quipgenkey.pem
```

## Debugging features

* You can just launch the AWS server by running `python deployquipgen.py justlaunch`, which will not start the quipgen server in the background and will increase the length of the instance self destruct timer.

## Installing Voice Synth (TEMP)

### From: https://github.com/CorentinJ/Real-Time-Voice-Cloning

source activate tensorflow_p36

git clone https://github.com/CorentinJ/Real-Time-Voice-Cloning
cd Real-Time-Voice-Cloning/
pip install -r requirements.txt
pip install unidecode inflect torch
sudo apt-get install libportaudio2
<<download pretrained.zip from https://williamkarnavas.com/voiceTransfer/pretrained.zip >>
unzip pretrained.zip
python demo_cli.py --no_sound

### From: https://github.com/fenceFoil/Real-Time-Voice-Cloning-Server

source activate tensorflow_p36

git clone https://github.com/fenceFoil/Real-Time-Voice-Cloning-Server
cd Real-Time-Voice-Cloning-Server/
pip install -r requirements.txt
sudo apt-get install libportaudio2
<<download pretrained.zip from https://williamkarnavas.com/voiceTransfer/pretrained.zip >>
<<download voice wav files?>>
unzip pretrained.zip
# Run flask server

### From nvidia

```bash
git clone https://github.com/NVIDIA/tacotron2.git
cd tacotron2
git submodule init; git submodule update
pip install torch apex
pip install -r requirements.txt

pip install tensorflow
# above did not work as planned as shown by pip freeze
conda install tensorflow
pip install unidecode inflect 
conda install llvmlite
pip install librosa tensorboardx

# At this point, "cannot find denoiser module"
# Solution from https://github.com/NVIDIA/tacotron2/issues/227
git pull origin master; git checkout 6188a1d106a1060336040db82f464d6441f39e21
# .. failed.
# From https://github.com/NVIDIA/tacotron2/issues/164
git submodule update --remote --merge

# module 'tensorflow' has no attribute 'contrib'
# error means we need to downgrade tensorflow from 2.0.0
conda install tensorflow=1.15

# For some reason after this procedure we got severely outdated versions of packages below
pip uninstall tensorboard tensorboardx
pip install tensorboard tensorboardx 

# Upgrade model: 
https://github.com/NVIDIA/waveglow/issues/154

cd waveglow
python convert_model.py ../waveglow_256channels_ljs_v2.pt ../waveglow_converted.pt
cd ..

jupyter notebook --ip=0.0.0.0 --port=31337
)
# Run on AWS EC2 AMI Machine Learning 25.3 ubuntu 16.04
# See pipfreeze.txt for working versions
# working with https://github.com/NVIDIA/tacotron2/commit/70d37f9e7d4a74ba4169b91114e936b446f79893

```

This time with a venv:

```bash
git clone https://github.com/NVIDIA/tacotron2.git
cd tacotron2
git submodule init
# From https://github.com/NVIDIA/tacotron2/issues/164
git submodule update --remote --merge

conda create -y --name tacotron_env python=3.6
source activate tacotron_env
conda install -y llvmlite tensorflow=1.15
pip install -r requirements.txt; pip install torch apex keras
# For some reason after this procedure we got severely outdated versions of packages below
pip uninstall -y numpy; pip install numpy
pip uninstall -y tensorboard tensorboardx; pip install tensorboard tensorboardx 

# Upgrade model: 
# https://github.com/NVIDIA/waveglow/issues/154

# Upload models at this point
#(Maybe have pi use SCP after getting an "alive" response back from flask, then convert model?)
cd waveglow; python convert_model.py ../waveglow_256channels.pt ../waveglow_converted.pt; cd ..

pip install ipykernel
python -m ipykernel install --user --name tacotron_env --display-name "Python (tacotron_env)"

jupyter notebook --ip=0.0.0.0 --port=31337

# Run on AWS EC2 AMI Machine Learning 25.3 ubuntu 16.04
# See pipfreeze.txt for working versions
# working with https://github.com/NVIDIA/tacotron2/commit/70d37f9e7d4a74ba4169b91114e936b446f79893

```

produced pipfreeze2.txt on 12/15/2019

Setup for quipgenserver-blue

FTP tacotron2_statedict.pt & waveglow_converted.pt into /home/ubuntu/

```bash

source /home/ubuntu/anaconda3/bin/activate tensorflow_p36p
# Download git repos
git clone https://github.com/fenceFoil/door-personality
git clone https://github.com/fenceFoil/tacotron2
# Install reqs for door-personality
cd door-personality/quipgen/
pip install -r requirements.txt
# Route traffic to the quipgen server's port
sudo iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8000

# Download and install tacotron2 server
# Move the speech server code into the tacotron2 dir
cp nvidiatacotron2server.py ../../tacotron2/nvidiatacotron2server.py
cd ../../tacotron2
git submodule init
git submodule update --remote --merge
conda create -y --name tacotron_env python=3.6
source activate tacotron_env
conda install -y llvmlite tensorflow=1.15
pip install -r requirements.txt
pip install torch apex keras soundfile flask
pip uninstall -y numpy; pip install numpy==1.17.4
pip uninstall -y tensorboard tensorboardx; pip install tensorboard tensorboardx 

# Start quipgen server!
cd /home/ubuntu/door-personality/quipgen/
source activate tensorflow_p36
gunicorn --bind 0.0.0.0:8000 quipgen2 &
# Start speech server
cd /home/ubuntu/tacotron2
source activate tacotron_env
gunicorn --bind 0.0.0.0:8001 nvidiatacotron2server &

# Packages were out of date and tacotron couldn't start
```

### Notes

If you use the VADER sentiment analysis tools, please cite:
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for
Sentiment Analysis of Social Media Text. Eighth International Conference on
Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.

> Thanks Hutto & Gilbert!