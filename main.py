import re
from nlp_api import *
from typing_extensions import Annotated
import string

patterns = {
    'smoker': r"sm.k.r|s.m.k.r\b",
    'dhumpai': r"d.m.a.|d..mp..|.om.a.|umpa.\b",
    'alchemy': r"al.k.m|.lch.m.\b",
    'benson': r"..ns.n\b",
    'goldleaf': r"go.lb|gol..lea.|g.l...|g.l../b",
    'dunhil': r"d.n.h.l|d.nh.l|.an.i.l|.an.i.l\b",
    'smooth': r".m..th|sm.d\b",
    'thanda_flvr': r"th.nd..fl.v|t.nd...fl.v|th.nd...fl.v|t.nd..fl.v|..de.fl.v|.and..fl.v|..anda.fl..\b",
    'best_tobacco': r".est.t.b..|.est..a.o|.est.o.a.o|.est.o.\b"
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
