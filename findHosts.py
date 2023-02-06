import json
import os
import numpy as np
import pandas as pd
import spacy
import truecase
import nltk
import re as reg
import extractor
import webscrape
from typing import Optional

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def doProcessing(s, hos_candidates):
    # if there is something captured
    #print(s)
    # print(win_candidates)
    if(s != None):
        string = s.string
        # print(string)
        a = truecase.get_true_case(string)
        doc = nlp(a)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if ent.text in hos_candidates:
                    hos_candidates[ent.text] += 1
                else:
                    hos_candidates[ent.text] = 1
    return

def findHosts(pandaf):

    hos_candidates = {}

    year = pandaf['timestamp_ms'][pandaf.shape[0]-1].year  # the year of the event NOTE: maybe add this to the event data structure?

    for i in range(pandaf.shape[0]):

        curr_text = pandaf['text'][i]
        # curr_text = GoogleTranslator(source='auto', target='english').translate(i_text)
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", "")
        curr_text = curr_text.replace("”", "")
        curr_text = curr_text.replace("-", "")

        pre_find1 = reg.search("\s+host", curr_text.lower()) # general one to have
        pre_find2 = reg.search("\s+should", curr_text.lower())
        pre_find3 = reg.search("\s+would", curr_text.lower())
        if pre_find1 != None and not pre_find2 and not pre_find3: 
            doProcessing(pre_find1, hos_candidates)
    ws = []
    if(hos_candidates != {}):
        
        print(hos_candidates)
        temp = max(hos_candidates, key = hos_candidates.get)
        if temp != None: 
            print(temp)
        ws.append(temp)
        del hos_candidates[max(hos_candidates, key=hos_candidates.get)]
        if hos_candidates != {}:
            sec_temp = max(hos_candidates, key = hos_candidates.get)
            if sec_temp != None: 
                print(sec_temp)
            ws.append(sec_temp)
            
    return ws

def main():
    # get the json twitter info
    p = os.path.dirname(os.path.realpath(__file__)) + r"/gg2013.json"

    pandaf = pd.read_json(p)
    temp = findHosts(pandaf)
    print(temp)

if __name__ == '__main__':
    main()
