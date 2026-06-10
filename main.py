import sys
import nltk
import random
import datetime
import difflib
from gtts import gTTS
import pygame
import os
import uuid
import speech_recognition as sr 
from jarvis_data import training_data
from getting_data import getting, day, date, commands , commands_2
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from ultralytics import YOLO
import cv2
import webbrowser
sys.path.append(r"C:\\Users\\Abhishek Jha\\Desktop\\jarvis_data.py")
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')

word = [x[0] for x in training_data]
labels = [x[1] for x in training_data]
vectorizer = CountVectorizer()
x = vectorizer.fit_transform(word)
model = MultinomialNB()
model.fit(x, labels)
datasets = [getting, day, date, commands,commands_2]
pygame.mixer.init()
def take_Commend():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("No speech detected...")
            return "None"

    try:
        print("Understanding...")
        text = r.recognize_google(audio, language='en-in')
        print("You said:", text)
        return text

    except sr.UnknownValueError:
        print("Could not understand audio")
        return "None"

    except sr.RequestError:
        print("Network error")
        return "None"
def speak(text):
    print("Jarvis:", text)

    filename = f"voice_{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.music.unload()
    os.remove(filename)
def find_reply(user_text):

    best_score = 0
    best_dataset = None
    best_key = None

    for data in datasets:
        for key in data.keys():

            score = difflib.SequenceMatcher(
                None,
                user_text.lower(),
                key.lower()
            ).ratio() * 100
      
            if score > best_score:
                best_score = score
                best_dataset = data
                best_key = key
    print("User:", user_text)
    print("Best Key:", best_key)
    print("Best Score:", best_score)
    if best_score >= 80:

        selected = random.choice(best_dataset[best_key])
  
        if isinstance(selected, tuple):
            reply, action = selected
        else:
            reply = selected
            action = None

        now = datetime.datetime.now()
        reply = reply.replace("[TIME]", now.strftime("%I:%M %p"))
        reply = reply.replace("[DATE]", now.strftime("%d %B %Y"))

        if action:
          try:
           action(user_text)
          except TypeError:
           action()
        return reply

    return None
lemmatizer = WordNetLemmatizer()
def replace_words(text):
    words = "youtube per search karo"
    words = "youtube per dekho"
    replace_words = text.replace(words," ").strip()
while True:

    text = take_Commend().lower()
    current_text = text
    if text == "None":
        continue

    words = word_tokenize(text)
    lem_word = []

    for w in words:
        lem_word.append(lemmatizer.lemmatize(w, pos='v'))

    processed_text = " ".join(lem_word)

    vec = vectorizer.transform([processed_text])
    pred = model.predict(vec)[0]

    reply = find_reply(text)
    
    if reply:
        speak(reply)
    else:
      speak("Soory! Did not understand")
