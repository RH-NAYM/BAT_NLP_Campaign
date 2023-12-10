# import asyncio
# import json
# import re
# import time
# from typing import List, Union

# import uvicorn
# import nltk
# import requests
# from fastapi import FastAPI
# from pydantic import BaseModel
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer

# # nltk.download('punkt')
# # nltk.download('stopwords')
# # nltk.download('wordnet')

# from api_secrets import API_KEY_ASSEMBLYAI

# app = FastAPI()

# CHUNK_SIZE = 5_242_880  # 5MB

# upload_endpoint = 'https://api.assemblyai.com/v2/upload'
# transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

# headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

# headers = {
#     "authorization": API_KEY_ASSEMBLYAI,
#     "content-type": "application/json"
# }


# class Item(BaseModel):
#     url: str


# def lemmatize_and_clean(text):
#     words = nltk.word_tokenize(text.lower())
#     words = [word for word in words if word.isalpha() and word not in set(stopwords.words('english'))]
#     lemmatizer = WordNetLemmatizer()
#     words = [lemmatizer.lemmatize(word) for word in words]
#     return ' '.join(words)


# # patterns = {
# #     'Unique Capsule': r"unique capsul|unit capsul|uniq...capsul|uni..capsul\b",
# #     'Refreshing Taste and Smell': r"refreshing taste smell|refreshing taste milk|refreshing test smell|ripe singh taste|repressing taste smell\b",
# #     'Benson & Hadges Breeze':r"\b(?:benson\s+h(?:ess|aze|ezes|edge)\s+breez|banson\s+(?:haze\s+breez|hedge\s+(?:breez|bre))|benson\s+h(?:aze\s+brie|edge\s+bridge))",
# # backup lst: r"\b(?:benson\s+h(?:ess|aze|age|ages|ezes|edge)\s+bre|banson\s+(?:haze\s+bre|hedge\s+(?:bre|bre))|benson\s+h(?:aze\s+brie|edge\s+bri))"
# # b2:r"(?:benson|banson\s+h(?:ess|aze|age|ages|ezes|edge)\s+(?:bre|bri))"
# # }  

# patterns = {
#     'Unique Capsule': r"\b(?:uni(?:que)?|unit|uniq\.+|uni\.+)\s*capsul",
#     'Refreshing Taste and Smell': r"\b(?:refreshing|ripe|repressing)\s+(?:taste\s+(?:smell|milk)|test\s+smell)",
#     'Benson & Hadges Breeze':r"\b(?:((b|p|v|f)(a|e).*?son)\s+(h(?:.*?))\s+(br))",
# }



# def nlp_bat(text):
#     results = {}
#     all_match = {}
#     for name, pattern in patterns.items():
#         matches = re.findall(pattern, text, re.IGNORECASE)
#         all_match[name] = matches
#         results[name] = len(matches)

#     print(all_match)
#     return results



# def read_file(filename):
#     with open(filename, 'rb') as f:
#         while True:
#             data = f.read(CHUNK_SIZE)
#             if not data:
#                 break
#             yield data


# def upload(filename):
#     upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
#     return upload_response.json()['upload_url']


# def transcribe(audio_url):
#     transcript_request = {'audio_url': audio_url}
#     transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
#     return transcript_response.json()['id']


# def poll(transcript_id):
#     polling_endpoint = f'{transcript_endpoint}/{transcript_id}'
#     polling_response = requests.get(polling_endpoint, headers=headers)
#     return polling_response.json()


# def get_transcription_result_url(url):
#     transcribe_id = transcribe(url)
#     while True:
#         data = poll(transcribe_id)
#         if data['status'] == 'completed':
#             return data, None
#         elif data['status'] == 'error':
#             return data, data['error']
#         print("Processing Audio")
#         time.sleep(2)


# def detect_audio(url, title):
#     data, error = get_transcription_result_url(url)
#     text_det = data['text']
#     print("main text : ",text_det)
#     lmtz = lemmatize_and_clean(text_det)
#     print("Clean text : ",lmtz)
#     txt = lmtz.lower()
#     r = nlp_bat(txt)
#     return r
# # def detect_audio(url, title):
# #     data, error = get_transcription_result_url(url)
# #     text_det = data['text']
# #     # print("Original Text:", text_det)
# #     lmtz = lemmatize_and_clean(text_det)
# #     # print("Lemmatized and Cleaned Text:", lmtz)
# #     txt = lmtz.lower()
# #     r = nlp_bat(txt)
# #     return r



# async def process_item(item: Item):
#     try:
#         print(item.url)
#         result = detect_audio(item.url, title="file")
#         result = json.dumps(result)
#         return json.loads(result)
#     finally:
#         pass


# async def process_items(items: Union[Item, List[Item]]):
#     if isinstance(items, list):
#         coroutines = [process_item(item) for item in items]
#         results_dict = await asyncio.gather(*coroutines)
#         results = {}
#         for item in results_dict:
#             results.update(item)
#     else:
#         results = await process_item(items)
#     return results


# @app.post("/nlp")
# async def create_items(items: Union[Item, List[Item]]):
#     try:
#         results = await process_items(items)
#         print("Result Sent to User:", results)
#         return results
#     finally:
#         pass


# if __name__ == "__main__":
#     try:
#         uvicorn.run(app, host="127.0.0.1", port=1111)
#     finally:
#         pass

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

from api_secrets import API_KEY_ASSEMBLYAI

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
    'Unique Capsule': r"\b(((u(?:nit|niq).*?)\s+(?:capsul))|(?:uni.capsul))",
    'Refreshing Taste and Smell': r"\b((((ref|rif|rip|rep).*?)\s+t(?:a|e|i|y)s.*?\s+sm(?:el|il|al|ol|.*?))|((?:in.*?)\s+t(?:a|e|i|y)s.*?\s+(?:mel|mil|mal|mol)))",
    'Benson & Hadges Breeze':r"\b((b|p|v|f)(?:(an|en|a|e)(?:s|ch)(?:on).*?)\s+h(?:.*?)\s+(b|p|v|f)(?:re|ee))",
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
    finally:
        pass


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=1111)
    finally:
        pass
