import pickle
import subprocess

from flask import Flask, jsonify, request

import run_generation

app = Flask(__name__)

@app.route('/gpt2')
def gpt2():
    prompt = "It's a beautiful day, and the door said, "
    subprocess.call('python run_generation.py --model_type gpt2 --model_name_or_path gpt2-medium --prompt "{}"'.format(prompt), shell=True)
    with open('run_generation_output.pkl', 'rb') as f:
        return jsonify(pickle.load(f))