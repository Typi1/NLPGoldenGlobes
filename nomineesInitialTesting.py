import json
import os
import numpy as np
import pandas as pd
import re as reg

def doProcessing(s, candidates, reverse: bool): # reverse specifies the direction in which strings are decomposed ex: if reverse, "i l y" -> {"i l y", "l y", "y"}. if not reverse, "i l y" -> {"i l y", "i l", "i"}
    # if there is something captured
    #print(s)
    # print(win_candidates)
    if(s != None and s.group(1) != None):
        num_wrds = len(reg.findall("(?:'|\w)+", s.group(1))) # the number of words in the phrase captured
        #print(reg.findall("(?:'|\w)+", s.group(1)))
        og_phrase = s.group(1).lower() # the phrase with consistent capitalization (lowercase)
        #print("OG: " + og_phrase)
        for i in range(num_wrds): # for each x words of the phrase (ex: for phrase "this is good" -> "this is good", "is good", "good")
            if reverse:
                if(num_wrds - i not in candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                    candidates[num_wrds - i] = {}
                search_res = reg.search("(?:(?:'|\w)+\s+){" + str(i) + "}((?:'|\w)+)*", og_phrase)
            else:
                i += 0
                if(i not in candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                    candidates[i] = {}
                search_res = reg.search("((?:(?:'|\w)+\s+){" + str(i) + "})", og_phrase)

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
                    candidates[num_wrds - i][search_res] = 1
                else:
                    candidates[num_wrds - i][search_res] += 1
            else:
                if(search_res not in candidates[i].keys()):
                    candidates[i][search_res] = 1
                else:
                    candidates[i][search_res] += 1
            #print(search_res)

            #print(num_wrds - i)
    return

p = os.path.dirname(os.path.realpath(__file__)) + r"\gg2013.json"

# testf = open(p)

# NOTE: for the imdb web scraping, the URL https://www.imdb.com/search/name/?match_all=true&start=0&ref_=rlm can be used
# where the start=X can be changed iteratively to get different actors at the top of the page (by popularity)

pandaf = pd.read_json(p)
print("number of data entries: " + str(pandaf.shape[0]))
print(pandaf['text'][pandaf.shape[0]-1]) # get the nth text entry
print(pandaf['timestamp_ms'][pandaf.shape[0]-1].year) # get the nth timestamp's year

candidates = {}

count = 0

for i in range(pandaf.shape[0]):
    curr_text = pandaf['text'][i].lower()
    # win_find1 = reg.search("[lL]incoln", curr_text) # general one to have
    # win_find2 = reg.search("[sS]eries", curr_text) # if we know award name OR nominee type (series)
    # win_find3 = reg.search("[cC]omedy", curr_text) # if we know award name
    # win_find4 = reg.search("[aA]ctress", curr_text) # if we know nominee type (not person)
    # win_find5 = reg.search("[aA]ctor", curr_text) # if we know nominee type (not person)
    # win_find6 = reg.search("mini-series", curr_text.lower())

    nom_find = {}

    rt = reg.search("^(?:rt)", curr_text)
    osc = reg.search("oscar", curr_text)
    # if(rt != None):
    #     print(rt.string)

    nom_find[1] = reg.search("\s+beat[s|\s*](?:out\s*)*\s*(['\w+\s*]+)", curr_text) # no reverse
    nom_find[2] = reg.search("(['\w+\s*]*)(?:really\s*|probably\s*|maybe\s*|potentially\s*|might\s*)*(?:just\s*|could\s*)*(?:potentially\s*|really\s*|maybe\s*|probably\s*|somehow\s*|might\s*)*\s+beat[s|\s*]", curr_text) # reverse
    nom_find[3] = reg.search("(['\w+\s*]*)should\s*(?:have|'ve)\s*w[io]n", curr_text) # reverse
    nom_find[4] = reg.search("(['\w+\s*]*)\s+(?:just\s*|\s*)(?:was|got)\s*(?:just\s*)*\s+robbed", curr_text) # reverse
    nom_find[5] = reg.search("(['\w+\s*]*)did(?:n't|\s+not)\s+win", curr_text) # reverse
    nom_find[6] = reg.search("(['\w+\s*]*)(?:was\s*|gets\s*|got\s*|getting\s*|is\s*)\s*snubbed", curr_text) # reverse
    nom_find[7] = reg.search("(?:pull|pray|hop|wish|expect)ing\s+(?:for|that|4)\s+(['\w+\s*]+)", curr_text) # no reverse
    nom_find[8] = reg.search("(?:pull|pray|hop|wish|expect)ing\s+(?!for|that|4)(['\w+\s*]+)", curr_text) # no reverse
    nom_find[9] = reg.search("c[o']*m[e\s+]*on\s+(['\w+\s*]+)", curr_text) # no reverse
    nom_find[10] = reg.search("(['\w+\s*]*)has\s+(?:a|the)\s+chance", curr_text) # not super important (few results) reverse
    nom_find[11] = reg.search("(?:hope|please)\s+(?!please)(?:that\s*|let\s*)*(['\w+\s*]+)win", curr_text)# reverse
    nom_find[12] = reg.search("^(?<!if)(['\w+\s*]*)was\s+nominated", curr_text) # reverse
    nom_find[13] = reg.search("(['\w+\s*]*)possibl", curr_text) # reverse
    nom_find[14] = reg.search("(['\w+\s*]*)los(?:t|es)", curr_text) # reverse
    nom_find[15] = reg.search("\s+los(?:t|es)\s+to\s+(['\w+\s*]*)", curr_text) # no reverse

    # nom_find[10] = reg.search("", curr_text)
    # nom_find[10] = reg.search("", curr_text)

    
    if(any(nom_find[x] != None for x in nom_find.keys()) and rt == None and osc == None):#win_find1 != None ):#and win_find2 != None and win_find3 == None and win_find4 == None and win_find5 != None and win_find6 == None):
        count += 1
        print(curr_text)
        for x in nom_find.keys():
            if nom_find[x] != None:
                print(str(x))
                rev = True
                match x:
                    case 2 | 3 | 4 | 5 | 6 | 10 | 11 | 12 | 13 | 14:
                        rev = True
                    case _: 
                        rev = False
                doProcessing(nom_find[x], candidates, rev)
                # candidates.append(nom_find[x].group(1).lstrip().rstrip())
        # candidates.append(nom_find[1].group(2))
        #s = reg.search("(\w+)\s+[lL]incoln\s+(\w+)", win_find1.string)#reg.search("(\w+)\s+[hH]ope\s+((?:\w+\s+)+)[wW]ins", win_find1.string)
        #print(s.string)
        #if(s != None):
        #    #print(s.group(1))
        #    candidates.append(s.group(1))
        #    candidates.append(s.group(2))

print(str(count))

# votes = {}
# for i in candidates:
#     if (not i in votes):
#         votes[i] = 1
#     else:
#         votes[i] += 1

# print(votes)
# print(max(votes, key = votes.get))

votes = {}
for i in candidates.keys():
    multiplier = 1.0
    if(i == 1):
        multiplier = 0.3
    for j in candidates[i].keys():
        if (not j in votes and candidates[i][j]):
            votes[j] = candidates[i][j] * multiplier

ws = None

print(votes)


if "" in votes:
    votes[""] = 0

if(votes != {}):
    temp = ""
    for i in range(100):
        temp = max(votes, key = votes.get)
        if temp != None: 
            print(temp)
            votes[temp] = 0
        else: print("OWWW")

#print(reg.search(r"[A-Z].*", "Les Misérables").group())

# dataf = json.load(testf)

# for iter in dataf[0]:
#     print(iter)

# testf.close()