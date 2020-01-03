# Start me with working directory inside root of nvidia tacotron 2 git project

# Imports for tacotron 2
import sys
sys.path.append('waveglow/')
import numpy as np
import torch

from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT, STFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence
from denoiser import Denoiser
import time
import os

# My server imports
import io
import soundfile
from flask import Flask, jsonify, request, send_file, make_response

# Load tacotron2 before starting server
# Setup code from inference.ipynb in nvidia tacotron2
hparams = create_hparams()
hparams.sampling_rate = 22050

# Wait for checkpoints to be uploaded before continuing
while not os.path.exists("models_uploaded.trigger"):
    time.sleep(1)

# Load model from checkpoint
checkpoint_path = "tacotron2_statedict.pt"
model = load_model(hparams)
model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
_ = model.cuda().eval().half()

# Load WaveGlow for mel2audio synthesis and denoiser
waveglow_path = 'waveglow_converted.pt'
waveglow = torch.load(waveglow_path)['model']
waveglow.cuda().eval().half()
for k in waveglow.convinv:
    k.float()
denoiser = Denoiser(waveglow)

# Server time!!
app = Flask(__name__)
application = app # For gunicorn to find

@app.route("/uptest")
def uptest():
    return "tacotron2 up!"

@app.route('/speak', methods=['POST'])
def speak():
    prompt = request.json["text"]
    
    # Prepare text input
    sequence = np.array(text_to_sequence(prompt, ['english_cleaners']))[None, :]
    sequence = torch.autograd.Variable(torch.from_numpy(sequence)).cuda().long()

    # Decode text input
    global model
    mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
    with torch.no_grad():
        audio = waveglow.infer(mel_outputs_postnet, sigma=0.666)
    #ipd.Audio(audio[0].data.cpu().numpy(), rate=hparams.sampling_rate)

    # Remove waveglow bias
    global denoiser
    audio_denoised = denoiser(audio, strength=0.1)[:, 0]
    #ipd.Audio(audio_denoised.cpu().numpy(), rate=hparams.sampling_rate)

    # Convert to ogg using pysoundfile into another memory array
    readwav = soundfile.SoundFile(io.BytesIO(np.swapaxes(audio_denoised.cpu().numpy(), 0, 1)), format="RAW", subtype="PCM_16", samplerate=22050, channels=1)
    oggout = io.BytesIO()
    # Ogg vorbis cut off the last couple of seconds on our very short voice clips
    soundfile.write(oggout, np.swapaxes(audio_denoised.cpu().numpy(), 0, 1), samplerate=22050, format="WAV")#,format="OGG" subtype="VORBIS")
        
    # Return this block of bytes over http
    oggout.seek(0)
    response = make_response(oggout.read())
    response.headers.set('Content-Type', 'audio/wav')
    return response