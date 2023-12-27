import asyncio
import json
import re
from typing import List, Union

import aiofiles
import uvicorn
import nltk
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging
import pytz
from datetime import datetime
from api_secrets import API_KEY_ASSEMBLYAI


# logging.basicConfig(filename0="BAT_NLP_Campaign.log",
#                     filemode='w')
# logger = logging.getLogger("BAT")
# logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler("BAT_NLP_Campaign.log")
# logger.addHandler(file_handler)
# total_done = 0
# total_error = 0



def get_bd_time():
    bd_timezone = pytz.timezone("Asia/Dhaka")
    time_now = datetime.now(bd_timezone)
    current_time = time_now.strftime("%I:%M:%S %p")
    return current_time

app = FastAPI()

CHUNK_SIZE = 5_242_880  # 5MB

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}


class Item(BaseModel):
    url: str


async def lemmatize_and_clean(text):
    words = nltk.word_tokenize(text.lower())
    words = [word for word in words if word.isalpha() and word not in set(stopwords.words('english'))]
    lemmatizer = WordNetLemmatizer()
    words = [await asyncio.to_thread(lemmatizer.lemmatize, word) for word in words]
    return ' '.join(words)


patterns = {
    'Unique Capsule': r"\b(((u(?:nit|niq).*?)\s+(?:capsul))|(?:.*?uni.*?capsul))",
    'Refreshing Taste and Smell': r"\b((((ref|rif|rip|rep|ep|pre).*?)\s+t(?:a|e|i|y)s(.*?)\s+(sm|(?:.*?(sm|m)))(?:el|il|al|ol|.*?))|((?:in.*?)\s+t(?:a|e|i|y)s.*?\s+(.*?)(sm|m)(?:el|il|al|ol|ail|eal)))",
    'Benson & Hadges Breeze':r"\b((b|p|v|f)(?:(an|en|a|e)(?:s|ch|t)(?:on|an|en).*?)\s+h(?:.*?)\s+(b|p|v|f)(?:re|ee|e|ri))",
}


async def nlp_bat(text): 
    results = {}
    all_match = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        all_match[name] = matches
        results[name] = len(matches)

    print(all_match)
    return results


async def read_file(filename):
    async with aiofiles.open(filename, 'rb') as f:
        while True:
            data = await f.read(CHUNK_SIZE)
            if not data:
                break
            yield data


async def upload(filename):
    async with httpx.AsyncClient() as client:
        async for data in read_file(filename):
            upload_response = await client.post(upload_endpoint, headers=headers_auth_only, data=data)
    return upload_response.json()['upload_url']


async def transcribe(audio_url):
    transcript_request = {'audio_url': audio_url}
    async with httpx.AsyncClient() as client:
        transcript_response = await client.post(transcript_endpoint, json=transcript_request, headers=headers)
    return transcript_response.json()['id']


async def poll(transcript_id):
    polling_endpoint = f'{transcript_endpoint}/{transcript_id}'
    async with httpx.AsyncClient() as client:
        polling_response = await client.get(polling_endpoint, headers=headers)
    return polling_response.json()


async def get_transcription_result_url(url):
    transcribe_id = await transcribe(url)
    while True:
        data = await poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']
        print("Processing Audio")
        await asyncio.sleep(2)


async def detect_audio(url, title):
    data, error = await get_transcription_result_url(url)
    text_det = data['text']
    print("main text : ", text_det)
    lmtz = await lemmatize_and_clean(text_det)
    print("Clean text : ", lmtz)
    txt = lmtz.lower()
    r = await nlp_bat(txt)
    return r


async def process_item(item: Item):
    try:
        print(item.url)
        result = await detect_audio(item.url, title="file")
        result = json.dumps(result)
        return json.loads(result)
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
    except Exception as e:
        # global total_error
        # total_error += 1
        # logger.info(f"Time:{get_bd_time()}, Execution Failed and Total Failed Execution : {total_error}, Payload:{items}, Response : {results}")
        # logger.error(str(e))
        return {"AI": f"Error: {str(e)}"}
    finally:
        # global total_done
        # total_done +=1
        # logger.info(f"Time:{get_bd_time()}, Execution Done and Total Successfull Execution : {total_done}, Payload:{items}, Response : {results}")
        pass


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=8020)
    finally:
        pass
