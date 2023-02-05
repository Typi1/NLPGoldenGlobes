import json
import os
import numpy as np
import pandas as pd
import re as reg
import extractor
import webscrape
from typing import Optional

# adds all relevant permutations of the capture group to the candidates dictionary along with the voting weight associated with the string
# it also groups permutations by the # of words in the string
# for example, the string "this is test" would lead to key-value pair candidates[3]["this is test"] += weight (= instead of += if "this is test" is not already a key)
# s is the search result
# candidates is a dictionary of dictionaries. the dictionary-typed values contain key-value pairs corresponding to strings of the same # of words. the values of said dictionaries have keys that are strings and values that are the accumulated weighted vote (before post-processing)
# reverse is a bool that specifies the direction in which strings are decomposed ex: if reverse, "i l y" -> {"i l y", "l y", "y"}. if not reverse, "i l y" -> {"i l y", "i l", "i"}
# weight is a float that gives the weighting of the votes (before taking into account length or other factors in post-processing of results)
def doProcessing(s, candidates, reverse: bool, weight: float): # reverse specifies the direction in which strings are decomposed ex: if reverse, "i l y" -> {"i l y", "l y", "y"}. if not reverse, "i l y" -> {"i l y", "i l", "i"}
    # if there is something captured
    print(s)
    # print(candidates)
    if(s != None and s.group(1) != None):
        num_wrds = len(reg.findall("(?:'|\*|\w)+", s.group(1))) # the number of words in the phrase captured
        #print(reg.findall("(?:'|\w)+", s.group(1)))
        og_phrase = s.group(1).lower() # the phrase with consistent capitalization (lowercase)
        print("OG: " + og_phrase)
        print(num_wrds)
        for i in range(num_wrds): # for each x words of the phrase (ex: for phrase "this is good" -> "this is good", "is good", "good")
            if reverse:
                if(num_wrds - i not in candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                    candidates[num_wrds - i] = {}
                search_res = reg.search("(?:(?:'|\*|\w)+\s+){" + str(i) + "}((?:'|\*|\w)+)*", og_phrase)
            else:
                i += 0
                if(i not in candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                    candidates[i] = {}
                search_res = reg.search("((?:(?:'|\*|\w)+\s+){" + str(i) + "})", og_phrase)

            gr = ""

            if search_res == None:
                continue
            
            gr = search_res.group(1)
    
            if gr == None: gr = ""
            # print(gr)
            if reverse:
                search_res = gr + search_res.string[search_res.span()[1]:] # get the first i words in the string before the "wins" instance
            else:
                search_res = gr
            search_res = search_res.lstrip().rstrip() # remove whitespaces at beginning and end of string
            if(reverse):
                if(search_res not in candidates[num_wrds - i].keys()):
                    candidates[num_wrds - i][search_res] = weight
                else:
                    candidates[num_wrds - i][search_res] += weight
            else:
                if(search_res not in candidates[i].keys()):
                    candidates[i][search_res] = weight
                else:
                    candidates[i][search_res] += weight
            #print(search_res)

            #print(num_wrds - i)
    return


# returns a proportion of keywords in the given string if that string is acceptable given a list of keywords and a threshold proportion (0 <= 1) of keywords that need to be included
# in simpler terms, if the proportion is less than the threshold, return 0. Return the actual proportion value otherwise.
# This proportion value can be used to weigh votes (strings with higher amounts of keywords matched have higher weighted votes)
# s is the string
# keywords is a list of strings (keywords to look for in the string s)
# threshold is the minimum proportion of keywords that need to be in s for this to return a nonzero value
def judgeKeywords(s: str, keywords: list, threshold: float):
    if threshold < 0 or threshold > 1:
        return 0
    
    prop = 0
    for x in keywords:
        if x in s:
            prop += 1.0

    prop /= float(len(keywords))

    if prop < threshold: prop = 0

    return prop

# takes a string and attempts a regex search on it.
# if there is a match, add it to the nom_results dict and then check the rest of the string for the same match until no matches are found, then return nom_results
def getMatches(s:str, nom_results:dict, num:int, rex:str, justremove: bool = False):
    # print(rex)
    # print(s)
    nom_results[num] = reg.search(rex, s)
    if nom_results[num] != None:
        if not justremove:
            nom_results = getMatches(s[nom_results[num].span()[1]:], nom_results, num + 100, rex, False)
        elif nom_results[num].group(1) != "":
            nom_results = getMatches(s[:nom_results[num].start(1)] + s[nom_results[num].end(1):], nom_results, num + 100, rex, True)
        else:
            nom_results = getMatches(s[nom_results[num].span()[1]:], nom_results, num + 100, rex, True)

    return nom_results

# # returns a list of strings from a pandas json read which match any of the regex checks inside
# def getRelevantStr(pandaf):

# returns a votes dictionary for different parts of lists including some target string(s)
def getLists(pandaf, curr_award, targets: list, rtOn: bool = True, list_seen: Optional[dict] = None):
    list_candidates = {}
    # loop through each tweet that isn't in seen (seen should be different than the main one used in findNominees)
    for i in range(pandaf.shape[0]):
        if list_seen != None and i in list_seen:
            continue
        curr_text = pandaf['text'][i].lower()
        list_find = {}

        # search for each target in the tweet
        for j in range(len(targets)):
            # if target string targets[j] is in the tweet, then run list comprehension
            if(targets[j].lower() in curr_text):
                # list_find = getMatches(curr_text, list_find, j*100 + 0, str("(['\w+\s*]*),\s*" + targets[j]))
                list_find = getMatches(curr_text, list_find, j*100 + 0, "(['\w+\s*]*)(?:,\s*(?:\w+\s+)*)+" + targets[j].lower(), True) # reverse
                list_find = getMatches(curr_text, list_find, j*100 + 1, targets[j].lower() + "(?:,\s*(?:\w+\s+)*?)+(['\w+\s*]*)", True) # reverse
                list_find = getMatches(curr_text, list_find, j*100 + 2, "(?:and)*(['\w+\s*]*?)(?:and\s*(?:\w+\s+)*?)+(?=" + targets[j].lower() + ")", True) # reverse
                list_find = getMatches(curr_text, list_find, j*100 + 3, "(?<=" + targets[j].lower() + ")\s*(?:and\s*(?:\w+\s+)*)+(?<=and)(['\w+\s*]+)", True) # no reverse
    
        # for each regex search criteria for a nominee (ex: X should have won)
        for x in list_find.keys():
            temp_ele = list_find[x]
            # if that expression was matched in the sentence, 
            if temp_ele != None:
                
                # print(temp_ele)
                # add the possible permutations of the following string to the nominee candidates using doProcessing, so that one of them should be the result
                rev = True
                match x % 100:
                    case 1 | 2 | 3 :
                        rev = True
                    case 4: 
                        rev = False
                        if "and" in temp_ele:
                            noAndEnd = reg.search("(['\w+\s*]+)and$", temp_ele)
                            if noAndEnd != None:
                                temp_ele = noAndEnd.group(1).rstrip()
                        
                doProcessing(temp_ele, list_candidates, rev, 0.5)

    return list_candidates





def findNominees(pandaf, curr_event, num, rtOn: bool = True, keyword_char_limit: int = 3, seen: Optional[dict] = None, top_candidate: Optional[str] = None):

    print(top_candidate)

    #print(events['event_nom'])

    nom_candidates = {}

    # threshold for proportion of keywords that have to be in a string for it to be evaluated
    threshold = 0.6

    # get the currently specified award name
    curr_award = curr_event.awards[list(curr_event.awards.keys())[num]]
    print(curr_award)

    # get a list of words (keywords) to search for from the award name
    keywords = reg.findall("\w{"+ str(keyword_char_limit) +"}\w+", curr_award.name.lower().replace("-", ""))
    

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

    # some keywords that are best to ignore since they are usually omitted or some other reason
    ignore_list = ["performance", "television", "motion", "picture", "original", "best", "role", "made", "feature", 'film']
    # print(ignore_list)

    # print(keywords)
    
    for x in ignore_list:
        if x in keywords:
            keywords.remove(x)

    print(keywords)

    year = pandaf['timestamp_ms'][pandaf.shape[0]-1].year  # the year of the event NOTE: maybe add this to the event data structure?

    new_seen = seen.copy()
    new_seen2 = seen.copy()

    print(exclude_list)

    win_count = 0 # number of times a tweet says that a movie has won X award
    win_threshold = 5 # threshold for win_count to equal/surpass for the program to assume the winner has been announced
    win_time = None # time that win_threshold is surpassed at (starts at None)
    min_after_threshold = 60000000000 * 5 # threshold maximum for the time after win_threshold is surpassed that tweets are "active" and more regex parses will apply.

    for i in range(pandaf.shape[0]):

        if(seen != None and i in seen):
            #if i % 1000 == 0: print(i)
            continue

        curr_text = pandaf['text'][i].lower()
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", "")
        curr_text = curr_text.replace("”", "")
        curr_text = curr_text.replace("-", "")
        curr_text = curr_text.replace("#", "")
        curr_text = curr_text.replace("’", "'")
        

        # if any of the explicitly excluded results are in the string, skip to the next string and don't waste any time on other searches for this string
        exclude_results = []
        for h in exclude_list:
            temp_ex = reg.search("(?:^|\s+|-|,|/|!|:)" + h + "(?:\s+|-|/|,|!|:|$)", curr_text.lower())
            
            if(temp_ex != None):
                exclude_results.append(temp_ex)
                break
        if(len(exclude_results) > 0):
            continue

        

        # creates a dictionary of regex search results for the string being evaluated. captured strings are potential nominees. there is only 1 capture group per value
        nom_find = {}
        nom_find = getMatches(curr_text, nom_find, 1, "\s+beat[s|\s*](?:out\s*)*\s*(['\w+\s*]+)") # no reverse
        # nom_find[1] = reg.search("\s+beat[s|\s*](?:out\s*)*\s*(['\w+\s*]+)", curr_text) # no reverse
        nom_find = getMatches(curr_text, nom_find, 2, "(['\w+\s*]*)(?:really\s*|probably\s*|maybe\s*|potentially\s*|might\s*)*(?:just\s*|could\s*)*(?:potentially\s*|really\s*|maybe\s*|probably\s*|somehow\s*|might\s*)*\s+beat[s|\s*]") # reverse
        # nom_find[2] = reg.search("(['\w+\s*]*)(?:really\s*|probably\s*|maybe\s*|potentially\s*|might\s*)*(?:just\s*|could\s*)*(?:potentially\s*|really\s*|maybe\s*|probably\s*|somehow\s*|might\s*)*\s+beat[s|\s*]", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 3, "(['\w+\s*]*)should\s*(?:have|'ve)\s*(?:w[io]n|gotten|got|been|be|get|snag|snagged)") # reverse
        # nom_find[3] = reg.search("(['\w+\s*]*)should\s*(?:have|'ve)\s*(?:w[io]n|gotten|got|been|be|get|snag|snagged)", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 4, "(['\w+\s*]*)\s+(?:just\s*|\s*)(?:was|got)\s*(?:just\s*)*\s+robbed") # reverse
        # nom_find[4] = reg.search("(['\w+\s*]*)\s+(?:just\s*|\s*)(?:was|got)\s*(?:just\s*)*\s+robbed", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 5, "(['\w+\s*]*)did(?:n't|\s+not)\s+win") # reverse
        # nom_find[5] = reg.search("(['\w+\s*]*)did(?:n't|\s+not)\s+win", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 6, "(['\w+\s*]*)(?:was\s*|gets\s*|got\s*|getting\s*|is\s*)\s*snubbed") # reverse
        # nom_find[6] = reg.search("(['\w+\s*]*)(?:was\s*|gets\s*|got\s*|getting\s*|is\s*)\s*snubbed", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 7, "(?:pull|pray|hop|wish|expect|want|root|cheer|deserve|deserv)(?:ing|ed)*\s+(?:for|that|4|it\s+is|it's|its|it\s+was|to)\s+(['\w+\s*]+)") # no reverse
        # nom_find[7] = reg.search("(?:pull|pray|hop|wish|expect|want|root|cheer|deserve|deserv)(?:ing|ed)*\s+(?:for|that|4|it\s+is|it's|its|it\s+was)\s+(['\w+\s*]+)", curr_text) # no reverse
        nom_find = getMatches(curr_text, nom_find, 8, "(?:pull|pray|hop|wish|expect|want|root|cheer|deserve|deserv)(?:ing|ed)*\s+(?!for|that|4|it\s+is|it's|its|it\s+was|to)(['\w+\s*]+)") # no reverse
        # nom_find[8] = reg.search("(?:pull|pray|hop|wish|expect|want|root|cheer|deserve|deserv)(?:ing|ed)*\s+(?!for|that|4|it\s+is|it's|its|it\s+was)(['\w+\s*]+)", curr_text) # no reverse
        nom_find = getMatches(curr_text, nom_find, 9, "c[o']*m[e\s+]*on\s+(['\w+\s*]+)") # no reverse
        # nom_find[9] = reg.search("c[o']*m[e\s+]*on\s+(['\w+\s*]+)", curr_text) # no reverse
        # nom_find = getMatches(curr_text, nom_find, 10, "(['\w+\s*]*)has\s+(?:a|the)\s+chance") # reverse
        # nom_find[10] = reg.search("(['\w+\s*]*)has\s+(?:a|the)\s+chance", curr_text) # not super important (few results) reverse
        nom_find = getMatches(curr_text, nom_find, 11, "(?:hope|please)\s+(?!please)(?:that\s*|let\s*)*(['\w+\s*]+)win") # reverse
        # nom_find[11] = reg.search("(?:hope|please)\s+(?!please)(?:that\s*|let\s*)*(['\w+\s*]+)win", curr_text)# reverse
        nom_find = getMatches(curr_text, nom_find, 12, "^(?<!if)(['\w+\s*]*)was\s+nominated") # reverse
        # nom_find[12] = reg.search("^(?<!if)(['\w+\s*]*)was\s+nominated", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 13, "(['\w+\s*]*)\s+possibl") # reverse
        # nom_find[13] = reg.search("(['\w+\s*]*)possibl", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 14, "(['\w+\s*]*)\s+los(?:t|es)") # reverse
        # nom_find[14] = reg.search("(['\w+\s*]*)\s+los(?:t|es)", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 15, "\s+los(?:t|es)\s+to\s+(['\w+\s*]*)") # no reverse
        # nom_find[15] = reg.search("\s+los(?:t|es)\s+to\s+(['\w+\s*]*)", curr_text) # no reverse

        nom_find = getMatches(curr_text, nom_find, 16, "(['\w+\s*]*)\s+(?:better)*\s*(?:not)*\s*w[oi]ns*") # reverse
        # nom_find[16] = reg.search("(['\w+\s*]*)\s+(?:better)*\s*(?:not)*\s*w[oi]ns*", curr_text) # reverse
        
        nom_find = getMatches(curr_text, nom_find, 19, "(?:why|how)\s+(?:(?:in)*\s*the\s*\w*)*\s*(?:did|has|was)\s+(['\w+\s*]+)") # no reverse
        # nom_find[19] = reg.search("(?:why|how)\s+(?:(?:in)*\s*the\s*\w*)*\s*(?:did|has|was)\s+(['\w+\s*]+)", curr_text) # no reverse
        nom_find = getMatches(curr_text, nom_find, 20, "(?:why|how)\s+(?:(?:in)*\s*the\s*\w*)*\s*(?!:did|has|was)\s+(['\w+\s*]+)") # no reverse
        # nom_find[20] = reg.search("(?:why|how)\s+(?:(?:in)*\s*the\s*\w*)*\s*(?!:did|has|was)\s+(['\w+\s*]+)", curr_text) # no reverse
        nom_find = getMatches(curr_text, nom_find, 21, "(['\w+\s*]*)\s+(?:was|is|were)\s+(?:the|a)*\s*(?:better|more|worse|less|terrible|bad|good|great|amazing|deserved|incredible|fantastic|best|worst|greatest|lamest|lame|boring|idiotic|absolutely|slog|bore|boring|rigged|unfortunate)") # reverse
        # nom_find[21] = reg.search("(['\w+\s*]*)\s+(?:was|is|were)\s+(?:the|a)*\s*(?:better|more|worse|less|terrible|bad|good|great|amazing|deserved|incredible|fantastic|best|worst|greatest|lamest|lame|boring|idiotic|absolutely|slog|bore|boring|rigged|unfortunate)", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 22, "(['\w+\s*]*)please") # reverse
        # nom_find[22] = reg.search("(['\w+\s*]*)please", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 23, "(['\w+\s*]*)(?:vs|v\.|versus)") # reverse
        # nom_find[23] = reg.search("(['\w+\s*]*)(?:vs|v\.|versus)", curr_text) # reverse
        nom_find = getMatches(curr_text, nom_find, 24, "(?:vs|versus|go|picks*)\s+(['\w+\s*]+)") # no reverse
        # nom_find[24] = reg.search("(?:vs|versus|go|picks*)\s+(['\w+\s*]+)", curr_text) # no reverse
        if top_candidate != None:
            nom_find = getLists(pandaf, curr_award, list(top_candidate), rtOn, seen)

        # if the award has probably just been given out, but only within a small range of time after, do more regex parses that can be less specific
        if win_time != None and pandaf['timestamp_ms'][i].value <= win_time + min_after_threshold:
            # create less specific regex parses
            nom_find = getMatches(curr_text, nom_find, 17, "(['\w+\s*]*)\s+[:;][\)\(DP\[\]X]") # reverse
            nom_find = getMatches(curr_text, nom_find, 18, "(['\w+\s*]*)\s+no+[\s\.\!$]") # reverse
            nom_find = getMatches(curr_text, nom_find, 25, "no+[\s\.\!$]*\s+(['\w+\s*]+)") # no reverse
            # nom_find[17] = reg.search("(['\w+\s*]*)\s+[:;][\)\(DP\[\]X]", curr_text) # reverse
            # nom_find[18] = reg.search("(['\w+\s*]*)\s+no+[\s\.\!$]", curr_text) # reverse
            # nom_find[25] = reg.search("no+[\s\.\!$]*\s+(['\w+\s*]+)", curr_text) # no reverse
            
        elif win_time != None and win_time > 0:
            win_time = - min_after_threshold
            print("\nEND OF WINNING TIME\n")
        

        rts = reg.search("^(?:[rR][tT])", curr_text)

        # if the string doesn't match any of the nominee finding regexes, add it to new_seen (which is returned at the end of evaluating this award to be used when evaluating for future awards)
        # also skip to the next string.
        if(all(nom_find[x] == None for x in nom_find.keys())):
            if new_seen == None:
                new_seen = {}
            new_seen[i] = curr_text
            continue            
        
        # get the proportion of the keywords that are in this string if they are above the threshold
        keyword_prop = judgeKeywords(curr_text.lower(), keywords, threshold)
        
        
        
        if(     # we don't need to check if at least 1 of the nominee finding regexes found something bc it checks that earlier
                (rtOn or rts == None) and # filters out (most) retweets if rtOn is False
                (keyword_prop > 0 or (win_time != None and pandaf['timestamp_ms'][i].value <= win_time + min_after_threshold)) # if the proportion of keywords in the string is higher than the threshold
                or (top_candidate != None and top_candidate in curr_text)
                ): 
            print(i)
            # print(pandaf['timestamp_ms'][i].value)
            # print(pandaf['timestamp_ms'][i])
            # if something probably actually won, then increment win_count
            if(win_count < win_threshold and nom_find[16] != None and keyword_prop > 0 and reg.search("^(?<!if)(['\w+\s*]*)\s+[wW]ins", curr_text) != None): 
                win_count += 1   
            # if we haven't already initialized win_time properly and win_count has now passed the threshold, initialize win_time with the current time
            if win_time == None and win_count >= win_threshold:
                win_time = pandaf['timestamp_ms'][i].value
                print("\nIT'S WINNING TIME\n")

            # adds text that was used to find a nominee for one award category to the seen list when going over later awards
            if new_seen2 == None:
                new_seen2 = {}
            new_seen2[i] = curr_text

            print(curr_text)

            # for each regex search criteria for a nominee (ex: X should have won)
            for x in nom_find.keys():
                # if that expression was matched in the sentence, 
                if nom_find[x] != None:
                    # add the possible permutations of the following string to the nominee candidates using doProcessing, so that one of them should be the result
                    rev = True
                    match x % 100:
                        case 2 | 3 | 4 | 5 | 6 | 10 | 11 | 12 | 13 | 14 | 16 | 17 | 18 | 21 | 22 | 23:
                            rev = True
                        case _: 
                            rev = False
                    if(x % 100 == 16): # weighs wins less because they are much more abundant
                        doProcessing(nom_find[x], nom_candidates, rev, (keyword_prop**2) / 3.0)
                    else:
                        doProcessing(nom_find[x], nom_candidates, rev, keyword_prop**2)

            # s = reg.search("(^[A-Z][\w+\s+]*)[wW]ins", win_find1.string) # captures the string starting with a capital letter in front of "[wW]ins"
            #s = reg.search("((?:[A-Z]\w*\s*)+)\s+[wW]ins", win_find1.string) # captures the sequence of all starting-with-capital-letter words in front of "[wW]ins" 
            
            
                #print(s.group(1))
                # search_result = 1# webscrape.imdb_type_check(s.group(1))
                # if(search_result != None):
                #     candidates.append(s.group(1))
    #print(win_candidates[1])
    #print(win_candidates.keys())


    votes = {}
    # i is the # of words in the string
    for i in nom_candidates.keys():
        multiplier = 1.0
        # if a string is a single word, weigh it less (mainly accounts for person names)
        if(i == 1):
            multiplier = 0.75
        # j is an actual key-value pair of string to weighted vote
        for j in nom_candidates[i].keys():
            if (not j in votes and nom_candidates[i][j]):
                votes[j] = nom_candidates[i][j] * multiplier

    ws = None

    

    if(votes != {}):
        if("" in votes.keys()):
            votes[""] = 0

        temp = max(votes, key = votes.get)
        if temp != None: print(temp)

        votes_list = list(votes.items())
        votes_list.sort(key=(lambda x: x[1]), reverse=True)
        print("votes ranking: " + str(votes_list))

        ws = max(votes, key = votes.get) # webscrape.imdb_type_check(max(votes, key = votes.get), year)


    # some backup for if the strings still left have extraneous stuff at the start and there are ties. 3-2 is for common string lengths of people names, 1 is for worst case scenario
    if ws == None and 3 in nom_candidates.keys():
        ws = max(nom_candidates[3], key = nom_candidates[3].get) # webscrape.imdb_type_check(max(nom_candidates[3], key = nom_candidates[3].get), year)
    if ws == None and 2 in nom_candidates.keys():
        ws = max(nom_candidates[2], key = nom_candidates[2].get) # webscrape.imdb_type_check(max(nom_candidates[2], key = nom_candidates[2].get), year)
    if ws == None and 1 in nom_candidates.keys():
        ws = max(nom_candidates[1], key = nom_candidates[1].get) # webscrape.imdb_type_check(max(nom_candidates[1], key = nom_candidates[1].get), year)

    # if there is some weirdness, try turning off retweets or varying the character minimum for keywords
    if ((votes == {} or ws == None) and rtOn and keyword_char_limit == 3 and top_candidate == None):
        (ws, new_seen) = findNominees(pandaf, curr_event, num, not rtOn, 3, new_seen)
    elif ((votes == {} or ws == None) and not rtOn and keyword_char_limit == 3 and top_candidate == None):
        (ws, new_seen) = findNominees(pandaf, curr_event, num, not rtOn, 4, new_seen)
    elif ((votes == {} or ws == None) and rtOn and keyword_char_limit == 4 and top_candidate == None):
        (ws, new_seen) = findNominees(pandaf, curr_event, num, not rtOn, 4, new_seen)
        

    # if nothing is found, run again without disregarding seen tweets
    if(votes == {} and seen != {} and ws == None and top_candidate == None):
        (ws, _) = findNominees(pandaf, curr_event, num, True, 3, {})

    print(findNominees(pandaf, curr_event, num, rtOn, keyword_char_limit, new_seen2, ws))
    

    for x in new_seen2.keys():
        if not x in new_seen.keys():
            new_seen[x] = new_seen2[x]

    return (ws, new_seen)

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

    curr_event = events['event_awa']

    award_names = list((list(curr_event.awards.keys())[x], x) for x in range(len(curr_event.awards.keys())))

    award_names.sort(key=lambda x: len(x[0]), reverse=True)

    #rint(award_names)

    # print(getMatches("i am imitator", {}, 1, "i(.{1})").items())
    
    seen = {}

    # list_test = getLists(pandaf, None, ["beat bill murray"], True, seen)

    # votes = {}
    # # i is the # of words in the string
    # for i in list_test.keys():
    #     multiplier = 1.0
    #     # if a string is a single word, weigh it less (mainly accounts for person names)
    #     if(i == 1):
    #         multiplier = 0.75
    #     # j is an actual key-value pair of string to weighted vote
    #     for j in list_test[i].keys():
    #         if (not j in votes and list_test[i][j]):
    #             votes[j] = list_test[i][j] * multiplier

    # ws = None

    

    # if(votes != {}):
    #     if("" in votes.keys()):
    #         votes[""] = 0

    #     temp = max(votes, key = votes.get)
    #     if temp != None: print(temp)

    #     votes_list = list(votes.items())
    #     votes_list.sort(key=(lambda x: x[1]), reverse=True)
    #     print("votes ranking: " + str(votes_list))
    
    # # (res, seen) = findNominees(pandaf, curr_event, 4, True, 3, seen)
    # # print(res)


    print(findNominees(pandaf, curr_event, 20, True, 3, seen)[0])
    
    # for i in award_names:#range(len(curr_event.awards.keys())):
    #     print("Award #" + str(i[1]) + ":")
    #     (temp, seen) = findWins(pandaf, curr_event, i[1], True, 3, seen)
    #     print(temp)
    # print(str(judgeKeywords("best performance by an actress in a television series - drama", ["actress", "series", "drama", "null"], 0.6)**2))
    # list_find = {}
    # tst_str = "a list, a set, an array, and test. but also a plane, a set, and a boat. list and array and set and probably and uh test and unlikely"
    # tar_str = "probably"
    
    # # list_find = getMatches(tst_str, list_find, 1, "(?!,).*,\s*(?:and)*\s*(['\w+\s*]*)", False)
    # # list_find = getMatches(tst_str, list_find, 2, "(?:,|\s+)and\s+([\w+\s*]+)", False)
    # # list_find = getMatches(tst_str, list_find, 3, "(['\w+\s*]*)and\s+", False)
    # list_find = getMatches(tst_str, list_find, 0, "(['\w+\s*]*)(?:,\s*(?:\w+\s+)*)+" + tar_str, True) # reverse
    # list_find = getMatches(tst_str, list_find, 1, tar_str + "(?:,\s*(?:\w+\s+)*?)+(['\w+\s*]*)", True) # reverse
    # list_find = getMatches(tst_str, list_find, 2, "(?:and)*(['\w+\s*]*?)(?:and\s*(?:\w+\s+)*?)+(?=" + tar_str + ")", True) # reverse
    # list_find = getMatches(tst_str, list_find, 3, "(?<=" + tar_str + ")\s*(?:and\s*(?:\w+\s+)*)+(?<=and)(['\w+\s*]+)", True) # no reverse
    # # list_find = getMatches(tst_str, list_find, 3, "(?<=" + tar_str + ")\s*(?:and\s*(?:\w+\s+)*)+?(?!\s*and\s*)(['\w+\s*]+)", True) # no reverse
    
    # for x in list_find.keys():
    #     if list_find[x] != None: 
    #         temp = list_find[x].group(1).lstrip().rstrip()
    #         if "and" in temp:
    #             noAndEnd = reg.search("(['\w+\s*]+)and$", temp)
    #             if noAndEnd != None:
    #                 temp = noAndEnd.group(1).rstrip()
    #         if(temp == ""): continue
    #         print(temp)

    # print(reg.search("(['\w+\s*]+)and$", "test to find if I can get rid of the 'and' at the end of a sentence and").group(1).rstrip())

if __name__ == '__main__':
    main()