import json
import os
import numpy as np
import pandas as pd
import spacy
import heapq
import truecase
import nltk
import re as reg
import webscrape
from typing import Optional

# made by Sean

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def doProcessing(s, pre_candidates, reverse: bool):
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
                if ent.text in pre_candidates:
                    pre_candidates[ent.text] += 1
                else:
                    pre_candidates[ent.text] = 1
    return

def findPres(pandaf, curr_award, keyword_char_limit: int = 3):

    pre_candidates = {}
    # print(curr_award)
    # get a list of words to search for from the award name
    keywords = reg.findall("\w{"+ str(keyword_char_limit) +"}\w+", curr_award.lower().replace("-", ""))
    # print(keywords)
    # some keywords that are best to ignore since they are usually omitted
    ignore_list = ["performance", "television", "motion", "picture", "original", "best", "role", "made"]
    # print(ignore_list)

    # some logic using the award name to exclude overlapping results (ex: best drama vs best actor in a drama)
    exclude_list = [" won ", "has won", " goes to "]
    if not "actor" in keywords:
        exclude_list.append("actor")
    if not "actress" in keywords:
        exclude_list.append("actress")
    if ("picture" in keywords or "movie" in keywords or "film" in keywords) and not "series" in keywords:
        exclude_list.append("series")
    if not "supporting" in keywords:
        exclude_list.append("supporting")

    for h in exclude_list:
        if h in keywords:
                keywords.remove(h)

    year = pandaf['timestamp_ms'][pandaf.shape[0]-1].year  # the year of the event NOTE: maybe add this to the event data structure?

    # print(exclude_list)
    # print(exclude_list)
    # print(keywords)
    # print(ignore_list)
    for i in range(pandaf.shape[0]):

        curr_text = pandaf['text'][i]
        # curr_text = GoogleTranslator(source='auto', target='english').translate(i_text)
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", "")
        curr_text = curr_text.replace("”", "")
        curr_text = curr_text.replace("-", "")
        curr_text = curr_text.replace("@", "")		
        curr_text = curr_text.replace("#", "")
        curr_text = curr_text.lower()

        pre_find1 = reg.search("present", curr_text) # general one to have

        exclude_results = []
        for h in exclude_list:
            temp_ex = reg.search(h, curr_text)
            exclude_results.append(temp_ex)
            if(temp_ex != None):
                break
        
        keyword_results = []
        for j in keywords:
            if(all(j != x for x in ignore_list)): 
                # result = j in curr_text.lower()
                # if not result:
                #     result = None
                result = reg.search(j, curr_text)
                keyword_results.append(result)
        
        
        if((    pre_find1 != None) and # checks the different variations of saying something has won
                # (rtOn or win_find10 == None) and # gets rid of (most) retweets
                # win_find6 == None and win_find7 == None and win_find8 == None and win_find9 == None and # gets rid of hopefuls and predictions
                all(x != None for x in keyword_results) and # award-specific keywords to look for
                all(x == None for x in exclude_results) # words to avoid (dependent on awards). Maybe combine with some stuff from above for conciseness later
                ): 

            doProcessing(pre_find1, pre_candidates, True)

    ws = []
    check = ["Actor", "Actress", "Producer", "Writer"]
    

    if(pre_candidates != {}):
        # print(pre_candidates)
        max_candidate = max(pre_candidates, key = pre_candidates.get)
        temp_res = webscrape.imdb_person_check(max_candidate, year)
        checker = True
        if temp_res:
            for i in range(pandaf.shape[0]):
                if temp_res[0] in pandaf['text'][i]:
                    checker = True
                    break
                else:
                    checker = False
        if checker == False: temp_res = None
        if temp_res == None:
            split = max_candidate.split()
            if len(split) > 2:
                temp_res = webscrape.imdb_person_check(split[0]+" "+split[1], year)
        while temp_res == None or temp_res[1] not in check:
            del pre_candidates[max(pre_candidates, key=pre_candidates.get)]
            if pre_candidates == {}:
                break
            max_candidate = max(pre_candidates, key = pre_candidates.get)
            temp_res = webscrape.imdb_person_check(max_candidate, year)
            checker = True
            if temp_res:    
                for i in range(pandaf.shape[0]):
                    if temp_res[0] in pandaf['text'][i]:
                        checker = True
                        break
                    else:
                        checker = False
            if checker == False: temp_res = None
            if temp_res == None:
                split = max_candidate.split()
                if len(split) > 2:
                    temp_res = webscrape.imdb_person_check(split[0]+" "+split[1], year)
        if pre_candidates != {} and temp_res[0].lower() not in curr_award:
            ws.append(temp_res[0])
            del pre_candidates[max(pre_candidates, key=pre_candidates.get)]
            if pre_candidates != {}:
                max_candidate = max(pre_candidates, key = pre_candidates.get)
                sec_temp_res = webscrape.imdb_person_check(max_candidate, year)
                checker = True
                if sec_temp_res:
                    for i in range(pandaf.shape[0]):
                        if sec_temp_res[0] in pandaf['text'][i]:
                            checker = True
                            break
                        else:
                            checker = False
                if checker == False: sec_temp_res = None
                if sec_temp_res == None:
                    split = max_candidate.split()
                    if len(split) > 2:
                        sec_temp_res = webscrape.imdb_person_check(split[0]+" "+split[1], year)
                if sec_temp_res != None and sec_temp_res[0] == temp_res[0]:
                    sec_temp_res = None
                while sec_temp_res == None or sec_temp_res[1] not in check:
                    del pre_candidates[max(pre_candidates, key=pre_candidates.get)]
                    if pre_candidates == {}:
                        break
                    max_candidate = max(pre_candidates, key = pre_candidates.get)
                    sec_temp_res = webscrape.imdb_person_check(max_candidate, year)
                    checker = True
                    if sec_temp_res:
                        for i in range(pandaf.shape[0]):
                            if sec_temp_res[0] in pandaf['text'][i]:
                                checker = True
                                break
                            else:
                                checker = False
                    if checker == False: sec_temp_res = None
                    if sec_temp_res == None:
                        split = max_candidate.split()
                        if len(split) > 2:
                            sec_temp_res = webscrape.imdb_person_check(split[0]+" "+split[1], year)
                    if sec_temp_res != None and sec_temp_res[0] == temp_res[0]:
                        sec_temp_res = None
                if sec_temp_res and sec_temp_res[0].lower() not in curr_award:
                    ws.append(sec_temp_res[0])
    return ws