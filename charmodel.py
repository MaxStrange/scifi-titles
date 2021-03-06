"""
Basic character model.

Stolen from keras: https://github.com/keras-team/keras/blob/master/examples/lstm_text_generation.py
"""
from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.callbacks import TensorBoard
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file

import argparse
import io
import numpy as np
import os
import random
import sys
import time

import data

def sample(preds, temperature=1.0):
    """
    Helper function to sample an index from a probability array
    """
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def predict(temperature, text, start_index, maxlen, chars, char_indices, model, indices_char, npreds=400, verbose=True):
    """
    Predict some text from the model.
    """
    if verbose:
        print('----- temperature:', temperature)
    generated = ''
    sentence = text[start_index: start_index + maxlen]
    generated += sentence
    if verbose:
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

    for _ in range(npreds):
        x_pred = np.zeros((1, maxlen, len(chars)))
        for t, char in enumerate(sentence):
            x_pred[0, t, char_indices[char]] = 1.

        preds = model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, temperature)
        next_char = indices_char[next_index]

        generated += next_char
        sentence = sentence[1:] + next_char

        if verbose:
            sys.stdout.write(next_char)
            sys.stdout.flush()
    if verbose:
        print()
    return generated

def setup():
    # Get the text from the the database
    text = '\n'.join([title for title in data.get_titles(limit=1E5)])

    # Get all the characters from the text
    chars = sorted(list(set(text)))

    # Create two maps: character to index and index to character
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    maxlen = 40
    step = 3

    return text, chars, char_indices, indices_char, maxlen, step

def train(model_path, nepochs):
    """
    Trains a model and saves it to disk.
    """
    text, chars, char_indices, indices_char, maxlen, step = setup()

    # Cut the text into fixed-length sequences
    sentences = []
    next_chars = []
    for i in range(0, len(text) - maxlen, step):
        sentences.append(text[i: i + maxlen])
        next_chars.append(text[i + maxlen])

    # Vectorize everything into numpy arrays
    x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
    y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
    for i, sentence in enumerate(sentences):
        for t, char in enumerate(sentence):
            x[i, t, char_indices[char]] = 1  # Each row is a sentence of the form: [45 92 32 19 etc.] where each number is a character id
        y[i, char_indices[next_chars[i]]] = 1  # Each row is a one-hot character vector

    # Build the super simple model - one LSTM layer and a character softmax output
    model = Sequential()
    model.add(LSTM(128, input_shape=(maxlen, len(chars))))
    model.add(Dense(len(chars)))
    model.add(Activation('softmax'))

    # Finish setting up the model #

    optimizer = RMSprop(lr=0.01)  # Probably swap this out with Adam and fiddle with the lr TODO
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)

    def on_epoch_end(epoch, logs):
        """
        Function invoked at end of each epoch.
        Prints generated text.
        """
        os.makedirs("models", exist_ok=True)
        if model_path is None:
            timestr = time.strftime("%I_%M%p_%b_%d_%Y")
            modelname = "models/{}.h5".format(timestr)
        else:
            modelname = model_path
        print("Saving model so far as: {}".format(modelname))
        model.save(modelname)
        print()
        print('----- Generating text after Epoch: %d' % epoch)

        start_index = random.randint(0, len(text) - maxlen - 1)
        for temperature in [0.2, 0.5, 1.0, 1.2]:
            predict(temperature, text, start_index, maxlen, chars, char_indices, model, indices_char)

    print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
    timestr = time.strftime("%I_%M%p_%b_%d_%Y")
    tb_callback = TensorBoard(log_dir="logs/objectid_" + timestr, write_grads=True, write_graph=True, write_images=True)

    # Train the model
    model.fit(x, y, batch_size=128, epochs=nepochs, callbacks=[print_callback, tb_callback])

def use(model_path, temperature, ntitles):
    """
    Load a model into memory and sample from it.
    """
    # Predict
    titles = set()
    itermax = ntitles  # We will run the network only this many times at most, which should be enough
    iteration = 0
    while len(titles) < ntitles and iteration < itermax:
        print("Getting a batch...")
        # Load the model - note that it is super inneficient to reload everything every iteration
        # But I don't have time to do things right
        model = load_model(model_path)

        # Set up
        text, chars, char_indices, indices_char, maxlen, _ = setup()
        start_index = random.randint(0, len(text) - maxlen - 1)

        text = predict(temperature, text, start_index, maxlen, chars, char_indices, model, indices_char, npreds=400, verbose=False)
        for t in text.split("\n"):
            titles.add(t.strip())
        print("Total number of titles generated so far:", len(titles))
        iteration += 1
    print("Here are your generated titles:")
    print("===========================")
    for i, title in enumerate(titles):
        if i >= ntitles:
            break
        print(title)

if __name__ == "__main__":
    def validate_temperature(t):
        try:
            t = float(t)
            if t <= 0.0:
                raise argparse.ArgumentTypeError()
            return t
        except:
            raise argparse.ArgumentTypeError("Temperature must be a positive number.")

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("train", "use"), default="train", help="train: Train the model; use: Use a trained model")
    parser.add_argument("--model", default=None, help="The name of the model: If we are training, this is where we will save it; if we are using, this is what we will load.")
    parser.add_argument("--temperature", type=validate_temperature, help="How diverse the output should be > 0")
    parser.add_argument("--n", type=int, default=100, help="The number of titles to generate")
    parser.add_argument("--epochs", type=int, default=5, help="The number of times to train on the data")
    args = parser.parse_args()

    if args.model is not None and not os.path.isfile(args.model):
        print("Model path {} is not a file.".format(args.model))
        exit(1)

    if args.mode == "train":
        train(args.model, args.epochs)
    else:
        use(args.model, args.temperature, args.n)
