import json
import os
import numpy as np
import pandas as pd
import re as reg
import extractor
import webscrape

def doProcessing(s, win_candidates):
    # if there is something captured
    #print(s)
    if(s != None and s.group(1) != None):
        num_wrds = len(reg.findall("\w+", s.group(1))) # the number of words in the phrase captured
        og_phrase = s.group(1).lower() # the phrase with consistent capitalization (lowercase)
        #print("OG: " + og_phrase)
        for i in range(num_wrds): # for each x words of the phrase (ex: for phrase "this is good" -> "this is good", "is good", "good")
            if(num_wrds - i not in win_candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                win_candidates[num_wrds - i] = {}
            
            search_res = reg.search("(?:\w+\s+){" + str(i) + "}(\w+)*", og_phrase)
            gr = search_res.group(1)
            if gr == None: gr = ""
            search_res = gr + search_res.string[search_res.span()[1]:] # get the first i words in the string before the "wins" instance
            search_res = search_res.lstrip().rstrip() # remove whitespaces at beginning and end of string
            
            if(search_res not in win_candidates[num_wrds - i].keys()):
                win_candidates[num_wrds - i][search_res] = 1
            else:
                win_candidates[num_wrds - i][search_res] += 1
            #print(search_res)

            #print(num_wrds - i)
    return

def findWins(pandaf, curr_event, num, rtOn: bool = True, keyword_char_limit: int = 3):

    

    #print(events['event_nom'])

    win_candidates = {}

    
    curr_award = curr_event.awards[list(curr_event.awards.keys())[num]]
    print(curr_award)

    # get a list of words to search for from the award name
    keywords = reg.findall("\w{"+ str(keyword_char_limit) +"}\w+", curr_award.name.lower().replace("-", ""))
    # print(keywords)

    # some keywords that are best to ignore since they are usually omitted
    ignore_list = ["performance", "television", "motion", "picture", "original", "best", "role", "made"]
    # print(ignore_list)

    # some logic using the award name to exclude overlapping results (ex: best drama vs best actor in a drama)
    exclude_list = []
    if not "actor" in keywords:
        exclude_list.append("actor")
    if not "actress" in keywords:
        exclude_list.append("actress")
    if ("picture" in keywords or "movie" in keywords or "film" in keywords) and not "series" in keywords:
        exclude_list.append("series")
    elif "miniseries" in keywords:
        exclude_list.append("series")
    if not "supporting" in keywords:
        exclude_list.append("supporting")

    for h in exclude_list:
        if h in keywords:
                keywords.remove(h)

    year = pandaf['timestamp_ms'][pandaf.shape[0]-1].year  # the year of the event NOTE: maybe add this to the event data structure?

    # print(exclude_list)

    for i in range(pandaf.shape[0]):
        curr_text = pandaf['text'][i]
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", "")
        curr_text = curr_text.replace("”", "")
        curr_text = curr_text.replace("-", "")

        win_find1 = reg.search("\s+[wW]ins", curr_text) # general one to have

        exclude_results = []
        for h in exclude_list:
            temp_ex = reg.search("(?:^|\s+|-|/)" + h + "(?:\s+|-|/|$)", curr_text.lower())
            exclude_results.append(temp_ex)
            if(temp_ex != None):
                break
            
            
        
        keyword_results = []
        for j in keywords:
            if(all(j != x for x in ignore_list)): 
                keyword_results.append(reg.search("(?:^|\s+|-|/)" + j + "(?:\s+|-|/|$)", curr_text.lower()))
        
        
        # win_find2 = reg.search("[sS]eries", curr_text) # if we know award name OR nominee type (series)
        # win_find3 = reg.search("[dD]rama", curr_text) # if we know award name
        # win_find4 = reg.search("[aA]ctress", curr_text) # if we know nominee type (not person)
        # win_find5 = reg.search("[aA]ctor", curr_text) # if we know nominee type (not person)
        win_find6 = reg.search("i\s+hope", curr_text.lower())
        win_find7 = reg.search("i\s+wish", curr_text.lower())
        win_find8 = reg.search("i\s+predict", curr_text.lower())
        win_find9 = reg.search("if\s+(?:\w+\s+)+wins", curr_text.lower())
        win_find10 = reg.search("^(?:RT)", curr_text)
        win_find11 = reg.search("\s+[wW]on\s+", curr_text)
        win_find12 = reg.search("\s+has\s+[wW]on\s+", curr_text)
        
        if((    win_find1 != None or win_find11 != None or win_find12 != None) and # checks the different variations of saying something has won
                (rtOn or win_find10 == None) and # gets rid of (most) retweets
                win_find6 == None and win_find7 == None and win_find8 == None and win_find9 == None and # gets rid of hopefuls and predictions
                all(x != None for x in keyword_results) and # award-specific keywords to look for
                all(x == None for x in exclude_results) # words to avoid (dependent on awards). Maybe combine with some stuff from above for conciseness later
                ): 
            #print(win_find1.string)
            if win_find1 != None:
                s = reg.search("([\w+\s+]*)[wW]ins", win_find1.string) # captures the string in front of "[wW]ins"
                #print(win_find1.string)
                doProcessing(s, win_candidates)
            if win_find12 != None:
                s = reg.search("([\w+\s+]*)has\s+won", win_find12.string.lower())
                # print(win_find12.string)
                doProcessing(s, win_candidates)
            elif win_find11 != None:
                s = reg.search("([\w+\s+]*?)[wW]on", win_find11.string) # captures the string in front of "[wW]on"
                # print("winfind11: " + win_find11.string)
                # print(s.span())
                # print(win_find11.string[0:win_find11.span()[0]] + win_find11.string[win_find11.span()[1]:])
                doProcessing(s, win_candidates)
            # s = reg.search("(^[A-Z][\w+\s+]*)[wW]ins", win_find1.string) # captures the string starting with a capital letter in front of "[wW]ins"
            #s = reg.search("((?:[A-Z]\w*\s*)+)\s+[wW]ins", win_find1.string) # captures the sequence of all starting-with-capital-letter words in front of "[wW]ins" 
            
            
                #print(s.group(1))
                # search_result = 1# webscrape.imdb_type_check(s.group(1))
                # if(search_result != None):
                #     candidates.append(s.group(1))
    #print(win_candidates[1])
    #print(win_candidates.keys())
    votes = {}
    for i in win_candidates.keys():
        multiplier = 1.0
        if(i == 1):
            multiplier = 0.3
        for j in win_candidates[i].keys():
            if (not j in votes and win_candidates[i][j]):
                votes[j] = win_candidates[i][j] * multiplier

    ws = None

    

    if(votes != {}):
        temp = max(votes, key = votes.get)
        if temp != None: print(temp)

        ws = webscrape.imdb_type_check(max(votes, key = votes.get), year)
    # if there is some weirdness, try turning off retweets
    if ((votes == {} or ws == None) and rtOn and keyword_char_limit == 3):
        ws = findWins(pandaf, curr_event, num, False, 3)
    elif ((votes == {} or ws == None) and not rtOn and keyword_char_limit == 3):
        ws = findWins(pandaf, curr_event, num, True, 4)
    elif ((votes == {} or ws == None) and rtOn and keyword_char_limit == 4):
        ws = findWins(pandaf, curr_event, num, False, 4)
        
    # some backup for if the strings still left have extraneous stuff at the start and there are ties. 3-2 is for common string lengths of people names, 1 is for worst case scenario
    if ws == None and 3 in win_candidates.keys():
        ws = webscrape.imdb_type_check(max(win_candidates[3], key = win_candidates[3].get), year)
    if ws == None and 2 in win_candidates.keys():
        ws = webscrape.imdb_type_check(max(win_candidates[2], key = win_candidates[2].get), year)
    if ws == None and 1 in win_candidates.keys():
        ws = webscrape.imdb_type_check(max(win_candidates[1], key = win_candidates[1].get), year)
    return ws

def main():
    # get the json twitter info
    p = os.path.dirname(os.path.realpath(__file__)) + r"\gg2013.json"

    pandaf = pd.read_json(p)
    #print("number of data entries: " + str(pandaf.shape[0]))
    #print(pandaf['text'][0]) # get the nth text entry
    #print(pandaf['timestamp_ms'][0]) # get the nth timestamp

    # get the extractor data structures up to the nominees data level

    parameters = extractor.load_json(os.path.dirname(os.path.realpath(__file__)) + r"\gg2013answers.json")
    events = extractor.input_parameters(parameters)

    curr_event = events['event_nom']

    # print(findWins(pandaf, curr_event, 21, True, 3))
    for i in range(len(curr_event.awards.keys())):
        print("Award #" + str(i) + ":")
        print(findWins(pandaf, curr_event, i, True, 3))

if __name__ == '__main__':
    main()