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

@app.route('/quip', methods=['GET','POST'])
def gpt2():
    prompt = "On that otherwise perfectly normal morning, the front door spoke, saying '"
    if 'prompt' in request.json:
        prompt = request.json['prompt']

    model_name = "distilgpt2"
    if 'modelName' in request.json:
        model_name = request.json['modelName']

    UNFILTERED_QUIP_POOL_SIZE = 10
    QUIPS_TAKEN_FROM_UNFILTERED_POOL = 1

    if 'unfilteredPoolSize' in request.json:
        UNFILTERED_QUIP_POOL_SIZE = request.json['unfilteredPoolSize']
    if 'takenFromEachPool' in request.json:
        QUIPS_TAKEN_FROM_UNFILTERED_POOL = request.json['takenFromEachPool']

    subprocess.call('python run_generation.py --seed {} --length 100 --model_type gpt2 --num_samples {} --model_name_or_path {} --prompt "{}"'.format(random.randint(0, 100000000), UNFILTERED_QUIP_POOL_SIZE, model_name, prompt), shell=True)
    with open('run_generation_output.pkl', 'rb') as f:
        generatedSamples = pickle.load(f)
    generatedSentences = [splitBySentences(s)[0] for s in generatedSamples]
    sortedSentences = sortSentencesBySentiment(generatedSentences)
    topSentences = sortedSentences[0:QUIPS_TAKEN_FROM_UNFILTERED_POOL]
    return jsonify(topSentences)
    
if __name__ == "__main__":
    app.run()