import os
import pandas as pd
import re as reg
from typing import Optional
import statistics
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# done by Ethan

def sentAnalysis(pandaf, target: str, rtOn: bool = False, seen: Optional[dict] = None):
    


    captures = []

    # iterate over tweets
    for i in range(pandaf.shape[0]):

        if i in seen.keys():
            continue

        curr_text = pandaf['text'][i]
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", " u201c ")
        curr_text = curr_text.replace("”", " u201c ")
        # curr_text = curr_text.replace("-", "")
        curr_text = curr_text.replace("#", "")
        curr_text = curr_text.replace("’", " u201c ")
        curr_text = curr_text.replace("‘", " u201c ")
        curr_text = curr_text.replace("@", "")
        
        if not rtOn:
            rt = reg.search("^(?:[rR][tT])\s+", curr_text) # reg.search("\s+(?:rt)\s+", curr_text)
            if rt == None:
                rt = reg.search("\s+(?:rt)\s+", curr_text)
            if rt == None and "u201c" in curr_text:
                rt = "not None"
            if rt == None and "http" in curr_text:
                rt = "not None"

        if not rtOn and rt != None:
            # if new_seen == None:
            #     new_seen = {}
            # new_seen[i] = curr_text
            continue

        

        if target.lower() in curr_text.lower().replace("best", "").replace("win", "").replace("won",""):
            captures.append(curr_text) 
            seen[i] = curr_text
        
    votes = []

    ana = SentimentIntensityAnalyzer()
    for cap in captures:
        vs = ana.polarity_scores(cap)
        # print(cap + ": " + str(vs['compound']))
        votes.append(vs['compound'])
        # print("{:-<65} {}".format(sentence, str(vs)))

    avg = sum(votes) / len(votes)

    return (avg, seen)


