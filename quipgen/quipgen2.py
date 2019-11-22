import pickle
import subprocess

from flask import Flask, jsonify, request

import run_generation

app = Flask(__name__)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sentimentAnalyzer = SentimentIntensityAnalyzer()
def sortSentencesBySentiment(sentences):
    global sentimentAnalyzer
    return sorted(sentences, key=lambda sentence: sentimentAnalyzer.polarity_scores(sentence)['compound'])

import nltk, nltk.data
def splitBySentences(text):
    nltk.download('punkt')
    tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)

@app.route('/gpt2')
def gpt2():
    prompt = "It's a beautiful day, and the door said, "
    subprocess.call('python run_generation.py --model_type gpt2 --num_samples 10 --model_name_or_path distilgpt2 --prompt "{}"'.format(prompt), shell=True)
    with open('run_generation_output.pkl', 'rb') as f:
        generatedSamples = pickle.load(f)
    generatedSentences = [splitBySentences(s)[0] for s in generatedSamples]
    return jsonify(sortSentencesBySentiment(generatedSentences))
    