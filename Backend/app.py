import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from datetime import datetime

from keras.models import load_model
model = load_model('model.h5')
import json
import random
intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl','rb'))
classes = pickle.load(open('labels.pkl','rb'))
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from concurrent.futures import ThreadPoolExecutor
import warnings
import os

warnings.filterwarnings("ignore")
app = Flask(__name__, template_folder='templates', static_folder='static')
os.path.dirname("../templates")

executor = ThreadPoolExecutor(max_workers=4)  # Adjust the number of workers as needed
   

# Fix the functions related to the chatbot
def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Modified bow function to ensure the bag has the correct dimensions
def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    
    # Print shape for debugging
    print(f"Input shape: {p.shape}")
    
    # Reshape input if needed to match model's expected input shape
    # This is a key fix - we need to ensure our input tensor matches what the model expects
    input_shape = model.input_shape[1]  # Get expected input dimension from model
    
    if len(p) != input_shape:
        print(f"Warning: Input dimension mismatch. Padding or truncating to {input_shape} features.")
        # Either pad with zeros or truncate to match expected input
        if len(p) < input_shape:
            # Pad with zeros
            p = np.pad(p, (0, input_shape - len(p)), 'constant')
        else:
            # Truncate
            p = p[:input_shape]
    
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        # Make sure we don't go out of bounds
        if r[0] < len(classes):
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    
    # Handle case where no intent matches the threshold
    if not return_list:
        return_list.append({"intent": "unknown", "probability": "0"})
        
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    # Handle unknown intents
    if tag == "unknown":
        return "I'm not sure I understand. Could you rephrase that?"
        
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    else:  # This executes if the for loop completes without a break
        result = "I'm not sure how to respond to that."
    return result

def chatbot_response(msg):
    try:
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)
        return res
    except Exception as e:
        print(f"Error in chatbot_response: {e}")
        return "Sorry, I encountered an error. Please try again."

@app.route("/")
@app.route("/dashboard")
def dashboard():
    # Add your dashboard route implementation
    return render_template("dashboard.html")

@app.route("/chat")
def home():
    return render_template("chat.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

if __name__ == "__main__":
    # Print model input shape for debugging
    print(f"Model expects input shape: {model.input_shape}")
    app.run(debug=True)
