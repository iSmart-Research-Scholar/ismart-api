from ntpath import join
from pytesseract import pytesseract
from PIL import Image
import requests
import os
from io import BytesIO
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
nltk.download('stopwords')

def teserract(url):
    pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'


    #Extract text from image
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(image)

    text = text.replace('\n',' ')
    
    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words() and len(word) > 2]
    text = ' '.join(tokens_without_sw)
    

    return text