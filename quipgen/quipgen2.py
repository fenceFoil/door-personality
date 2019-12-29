import pickle
import subprocess
import random

from flask import Flask, jsonify, request

import run_generation

app = Flask(__name__)
application = app # Provide application for gunicorn

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sentimentAnalyzer = SentimentIntensityAnalyzer()
def sortSentencesBySentiment(sentences):
    global sentimentAnalyzer
    return sorted(sentences, reverse=True, key=lambda sentence: sentimentAnalyzer.polarity_scores(sentence)['compound'])

import nltk, nltk.data
nltk.download('punkt')
def splitBySentences(text):
    tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)

@app.route("/uptest")
def uptest():
    return "server up!"

@app.route('/gpt2')
def gpt2():
    NUM_TEXT_SAMPLES = 10
    NUM_QUIPS_RETURNED = 1
    prompt = "On that otherwise perfectly normal morning, the front door spoke, saying '"

    subprocess.call('python run_generation.py --seed {} --length 100 --model_type gpt2 --num_samples {} --model_name_or_path distilgpt2 --prompt "{}"'.format(random.randint(0, 100000000), NUM_TEXT_SAMPLES, prompt), shell=True)
    with open('run_generation_output.pkl', 'rb') as f:
        generatedSamples = pickle.load(f)
    generatedSentences = [splitBySentences(s)[0] for s in generatedSamples]
    sortedSentences = sortSentencesBySentiment(generatedSentences)
    topSentences = sortedSentences[0:NUM_QUIPS_RETURNED]
    return jsonify(topSentences)
    
if __name__ == "__main__":
    app.run()