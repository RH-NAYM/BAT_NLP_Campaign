import re
from nlp_api import *
from typing_extensions import Annotated
import string

patterns = {
    'Unique Capsule': r"unique capsul|unit capsul|uniq...capsul|uni..capsul\b",
    'Refreshing Taste and Smell': r"refreshing taste smell|refreshing taste milk|refreshing test smell|ripe singh taste|repressing taste smell\b",
    'Benson & Hadges Breeze': r"benson he.es breez|benson hess breez|benson he..e breez|benson haze breez|benson hezes bee|banson breez|banson hedge breathe|banson hedge bridge|benson hedge bre|benson hedge bridge| benson haze brie|banson haze breeze|banson hedge breez\b"
}


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


# # input
filename = input("Give Audio Name: ")
audio_url = upload(filename)


# # transcribe
detect_audio(audio_url, 'file_title')
# print(text_det)
# print("xxxxxxxxx",text_det)
# text = text_det
# print(text)/
# result = nlp_bat(text)
# print(result)

# print(result)
# print(text)
