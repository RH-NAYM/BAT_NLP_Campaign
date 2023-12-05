# files after part 2
import requests
import time
from api_secrets import API_KEY_ASSEMBLYAI
import re
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from typing import List, Union
import uvicorn
import json
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')



app = FastAPI()

class Item(BaseModel):
    url: str

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB

def lemmatize_and_clean(text):
    # Tokenize the text into words
    words = nltk.word_tokenize(text)

    # Remove punctuation and convert to lowercase
    words = [word.lower() for word in words if word.isalpha()]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Lemmatize the words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # Join the words back into a cleaned text
    cleaned_text = ' '.join(words)

    return cleaned_text

# Patterns
# patterns = {
#     'smoker': r"sm.k.r|s.m.k.r\b",
#     'dhumpai': r"d.m.a.|d..mp..|.om.a.|umpa.\b",
#     'alchemy': r"al.k.m|.lch.m.\b",
#     'benson': r"..ns.n\b",
#     'goldleaf': r"go.lb|gol..lea.|g.l...|g.l../b",
#     'dunhil': r"d.n.h.l|d.nh.l|.an.i.l|.an.i.l\b",
#     'smooth': r".m..th|sm.d\b",
#     'thanda_flvr': r"th.nd..fl.v|t.nd...fl.v|th.nd...fl.v|t.nd..fl.v|..de.fl.v|.and..fl.v|..anda.fl..\b",
#     'best_tobacco': r".est.t.b..|.est..a.o|.est.o.a.o|.est.o.\b"
# }
# patterns = {
#     'Unique Capsule': r"unique capsul|unit capsul|uniq...capsul|uni..capsul\b",
#     'Refreshing Taste and Smell': r"refreshing taste smell|refreshing taste milk\b",
#     'Benson & Hadges Breeze': r"benson he.es breez|benson hess breez|benson he..e breez|benson haze breez|benson hezes bee|banson breez|banson hedge breathe|banson hedge bridge|benson hedge bre|benson hedge bridge\b"
# }

patterns = {
    'Unique Capsule': r"unique capsul|unit capsul|uniq...capsul|uni..capsul\b",
    'Refreshing Taste and Smell': r"refreshing taste smell|refreshing taste milk|refreshing test smell|ripe singh taste|repressing taste smell\b",
    'Benson & Hadges Breeze': r"benson.hage.bree|benson.hage..bree|banson.hage.bree|banson.hage..bree|benson he.es breez|benson hess breez|benson he..e breez|benson haze breez|benson hezes bee|banson breez|banson hedge breathe|banson hedge bridge|benson hedge bre|benson hedge bridge| benson haze brie|banson haze breeze|banson hedge breez\b"
}
# patterns = {
#     'Unique Capsule': r'\b(?:uni(?:que)?|unit|uniq\.+|uni\.+)\s*capsul\b',
#     'Refreshing Taste and Smell': r'\b(?:refreshing|ripe|repressing)\s+(?:taste\s+(?:smell|milk)|test\s+smell)\b',
#     'Benson & Hadges Breeze': r'\b(?:benson\s+h(?:ess|aze|ezes|edge)\s+breez|banson\s+(?:haze\s+breez|hedge\s+(?:breez|bre))|benson\s+h(?:aze\s+brie|edge\s+bridge))\b',
# }
# Find and count matches for each pattern
def nlp_bat(text):
    results = {}
    all_match = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        m = {name:matches}
        all_match.update(m)
        count = len(matches)
        results[name] = count
    
    
    print(all_match)    

    return results






def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    transcript_request = {
        'audio_url': audio_url
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    return transcript_response.json()['id']

        
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result_url(url):
    transcribe_id = transcribe(url)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']
            
        print("Processing Audio")
        time.sleep(2)
        
        
def detect_audio(url, title):
    data, error = get_transcription_result_url(url)
    text_det = data['text']
    lmtz = lemmatize_and_clean(text_det)
    print(lmtz)
    txt = lmtz.lower()
    r = nlp_bat(txt)
    # print(txt)
    # print(r)
    return r


async def process_item(item: Item):
    try:
        print(item.url)
        result = detect_audio(item.url,title="file")
        result = json.dumps(result)
        res = json.loads(result)
        return res
    finally:
        pass

async def process_items(items: Union[Item, List[Item]]):
    if isinstance(items, list):
        coroutines = [process_item(item) for item in items]
        results_dict = await asyncio.gather(*coroutines)
        results = {}
        for item in results_dict:
            results.update(item)
    else:
        results = await process_item(items)
    return results
 
@app.post("/nlp")
async def create_items(items: Union[Item, List[Item]]):
    try:
        results = await process_items(items)
        print("Result Sent to User:", results)
        return results
    finally:
        pass

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=8020)
    finally:
        pass
