import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import json
import pickle
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
import random

# Download NLTK resources if not already done
nltk.download("punkt")  # Corrected from "punkt_tab" to "punkt"
nltk.download("wordnet")  # Added wordnet download for lemmatization

lemmatizer = WordNetLemmatizer()

words = []
classes = []
documents = []
ignore_words = ['?', '!']
data_file = open('data.json').read()
intents = json.loads(data_file)

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Tokenize each word
        w = word_tokenize(pattern)
        words.extend(w)
        # Add documents in the corpus
        documents.append((w, intent['tag']))

        # Add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Lemmatize and lower each word and remove duplicates
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# Sort classes
classes = sorted(list(set(classes)))

# Documents = combination between patterns and intents
print(len(documents), "documents")
# Classes = intents
print(len(classes), "classes", classes)
# Words = all words, vocabulary
print(len(words), "unique lemmatized words", words)

# Save words and classes
pickle.dump(words, open('texts.pkl', 'wb'))
pickle.dump(classes, open('labels.pkl', 'wb'))

# Create our training data
training = []
# Create an empty array for our output
output_empty = [0] * len(classes)
# Training set, bag of words for each sentence
for doc in documents:
    # Initialize our bag of words
    bag = []
    # List of tokenized words for the pattern
    pattern_words = doc[0]
    # Lemmatize each word - create base word, in attempt to represent related words
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # Create our bag of words array with 1, if word match found in current pattern
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    
    # Output is a '0' for each tag and '1' for current tag (for each pattern)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    
    training.append([bag, output_row])

# Shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training, dtype=object)

# Separate features and labels
train_x = np.array([item[0] for item in training])
train_y = np.array([item[1] for item in training])

print("Training data created")

# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Fit and save the model
hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
model.save('model.h5')

print("Model created")