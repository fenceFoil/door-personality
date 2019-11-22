import pickle

from flask import Flask, jsonify, request

import run_generation

app = Flask(__name__)

@app.route('/gpt2')
def gpt2():
    with open('run_generation_output.pkl', 'r') as f:
        return jsonify(pickle.load(f))