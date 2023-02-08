import os
import numpy as np
import pandas as pd
import re as reg
import extractor
import webscrape
from typing import Optional
import statistics

# Made by Ethan

def doProcessing2(s, candidates, reverse: bool, weight: float = 1): # reverse specifies the direction in which strings are decomposed ex: if reverse, "i l y" -> {"i l y", "l y", "y"}. if not reverse, "i l y" -> {"i l y", "i l", "i"}
    # if there is something captured
    # print(s)
    # print(candidates)
    if(s != None and s.group(1) != None):
        num_wrds = len(reg.findall("(?:'|\*|\w|\-)+", s.group(1))) # the number of words in the phrase captured
        #print(reg.findall("(?:'|\w)+", s.group(1)))
        og_phrase = s.group(1) # the phrase with consistent capitalization (lowercase)
        if not reverse:
            og_phrase = og_phrase + " a"
            num_wrds += 1
        # print("OG: " + og_phrase)
        # print(num_wrds)
        for i in range(num_wrds): # for each x words of the phrase (ex: for phrase "this is good" -> "this is good", "is good", "good")
            if reverse:
                if(num_wrds - i not in candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                    candidates[num_wrds - i] = {}
                search_res = reg.search("(?:(?:'|\*|\w|\-)+\s+){" + str(i) + "}((?:'|\*|\w|\-)+)*", og_phrase)
            else:
                i += 0
                if(i not in candidates.keys()): # if there isn't a dictionary key for this # of words, add an entry corresponding to it
                    candidates[i] = {}
                search_res = reg.search("((?:(?:'|\*|\w|\-)+\s+){" + str(i) + "})", og_phrase)

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
    # if "weaver" in s.string.lower(): 
    #     print(s.string.lower())
    #     print(candidates[2])
    return candidates

# if a winner string doesn't give a match in imdb, try adding spaces in it, starting from the end to the beginning (last names are more likely to have hyphens than first names)
def trySpaces(s: str, year):
    if(len(s) < 1):
        return None
    ws = None
    for ii in reversed(range(len(s))):
        if(ii == 0):
            continue
        if s[ii] != " " and s[ii-1] != " ":
            # print(s[ii])
            test_str = s[:ii] + " " + s[ii:]
            ws = webscrape.imdb_type_check(test_str, year)
        if ws != None: break
    return ws

# get the quartiles of timestamps of appearances of the target string in tweets
def getQTS(pandaf, target_str: str, rtOn: bool = False):
    times = []
    # runs through every tweet
    for i in range(pandaf.shape[0]):
        curr_text = pandaf['text'][i].lower()
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", " u201c ")
        curr_text = curr_text.replace("”", " u201c ")
        # curr_text = curr_text.replace("-", "")
        curr_text = curr_text.replace("#", "")
        curr_text = curr_text.replace("’", " u201c ")
        curr_text = curr_text.replace("‘", " u201c ")

        if not rtOn:
            rt = reg.search("^(?:[rR][tT])\s+", curr_text) # reg.search("\s+(?:rt)\s+", curr_text)
            if rt == None:
                rt = reg.search("\s+(?:rt)\s+", curr_text)
            if rt == None and "u201c" in curr_text:
                rt = "not None"

        if not rtOn and rt != None:
            # if new_seen == None:
            #     new_seen = {}
            # new_seen[i] = curr_text
            continue

        if target_str.lower() in curr_text:
            times.append(pandaf['timestamp_ms'][i].value)

    qts = []
    if(len(times) >= 2): qts = statistics.quantiles(times)
    elif(len(times) == 1): qts = [times[0]]

    return qts
    
# returns true if string is only made of common words
def isCommon(s:str):
    common_wrds = ["i", "it", "is", "st", "you", "u", "blah", "of", "the", "if", "what", "why", "to", "a", "an", "are", "for", "that", "its", "do", "can", "those", "these", "win", "but", "in", "out", "or", "tv", "series", "on", "ugh", "this", "go", "wow", "duh", "um", "she", "he", "her", "hers", "his", "well", "just", "really", "totally", "so", "and", "someone", "somebody", "again", "good", "bad"]
    wrds = reg.findall("(?=(?<!\w)(\w+)(?:\W|$))", s)
    return all((x.lower().lstrip().rstrip() in common_wrds) for x in wrds)

def getMatches(s:str, nom_results:dict, num:int, rex:str, justremove: bool, shorthand:str = ""):
    # print(rex)
    # way to speed up output by making not all text strings need to go through regex searches
    if shorthand != "" and not shorthand in s.lower():
        return nom_results
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

def getWSResults(target: str, year: Optional[int] = None):
    ws = None
    if year != None:
        ws = webscrape.imdb_type_check(target, year)
    else:
        ws = webscrape.imdb_type_check(target, 0)
    return ws

# returns boolean of whether s is a substring of a nominee in the list
def isSubstring(s: str, noms: list):
    return any(s in x for x in noms)


def addPermutations(s:str, ws, ws_seen):
    wrds = reg.findall("(?=(?<!\w)(\w+)(?:\W|$))", s)
    if ws == None or ws[0] == None: return ws_seen
    if ws_seen == None: ws_seen = {}
    # print(wrds)
    for x in range(len(wrds)):
        temp = reg.search("((?:\w+\!*\-*\:*\.*\,*\(*\)*\s*){" + str(x) + "})",s)
        # print(temp)
        if temp != None and temp.group(1) != "" and temp.group(1).lstrip().rstrip() != None and not isCommon(temp.group(1)):
            ws_seen[temp.group(1).lstrip().rstrip()] = ws[0]
    for x in range(len(wrds)):
        if(x == 0): continue
        temp = reg.search("(?:\w+\!*\-*\:*\.*\,*\(*\)*\s*){" + str(x) + "}((?:\w+\!*\-*\:*\.*\,*\(*\)*\s*)*)",s)
        # print(temp.group(1))
        if temp != None and temp.group(1) != "" and temp.group(1).lstrip().rstrip() != None and not isCommon(temp.group(1)):
            ws_seen[temp.group(1).lstrip().rstrip()] = ws[0]

    return ws_seen


def compileNominees(candidates: list, year: Optional[int] = 0, winner: Optional[str] = None, ws_seen: Optional[dict] = {}):

    # get the winner type
    winner_ws = getWSResults(winner, year)
    if winner_ws == None:
        winner_ws = trySpaces(winner, year)
    

    nom_type = winner_ws[1]

    # determine the type that nominees must be: content, person, actor, or actress
    # content-types cannot win for person, actor, or actress typed awards
    # person-types cannot win for content, actor, or actress typed awards
    # actor-types cannot win for content or actress typed awards. They can win for person typed awards though.
    # actress-types cannot win for content or actor typed awards. They can win for person typed awards though.
    if type(nom_type) == list:
        nom_type = "content"
    elif nom_type != "Actor" and nom_type != "Actor":
        nom_type = "person"

    ws_seen[winner] = (winner_ws[0], nom_type)

    # nominees = []
    nominees_ws = []

    if winner != None and not winner in nominees_ws:
        nominees_ws.append(winner.title())

    max_noms = 4
    max_search_depth = 10

    counter2 = 0

    # print(reg_noms)
    # print(list_noms)

    # print("webscraping")

    
    
    # if the type is actor, actress, or person
    if nom_type != "content":
        for i in range(len(candidates)):
            # print(reg_noms[i][0])
            # print(year)

            # nom_type != "content" and nom_type == ws1[1])

            if candidates[i][0] != None and len(reg.findall("(?=(?<!\w)(\w+)(?:\W|$))", candidates[i][0])) < 4:
                if isSubstring(candidates[i][0], nominees_ws):
                    continue
                # if we haven't encountered this name, webscrape and add it to ws_seen
                if not candidates[i][0] in ws_seen.keys():
                    ws1 = webscrape.imdb_type_check(candidates[i][0], 0)
                    # ws1 = getWSResults(candidates[i][0], year)
                    ws_seen[candidates[i][0]] = ws1
                    ws_seen = addPermutations(candidates[i][0], ws1, ws_seen)
                # if we have seen it already, just access its value from ws_seen
                else:
                    ws1 = ws_seen[candidates[i][0]]

                # if the nominee type is either actor or actress, we must exclude those of the other type from nominee list
                if nom_type == "Actress":
                    if ws1 != None and not ws1[0] in nominees_ws and (nom_type == ws1[1] or (ws1[1] != "Actor" and type(ws1[1]) != list)) and not isSubstring(ws1[0], nominees_ws) and reg.search("f.ck", ws1[0].lower()) == None and len(reg.findall("(?=(?<!\w)(\w+)(?:\W|$))", ws1[0])) < 4: # last part here is to edit out profanity in results
                        # nominees_ws.append(ws1[0])
                        nominees_ws.append(candidates[i][0])
                elif nom_type == "Actor":
                    if ws1 != None and not ws1[0] in nominees_ws and (nom_type == ws1[1] or (ws1[1] != "Actress" and type(ws1[1]) != list)) and not isSubstring(ws1[0], nominees_ws) and reg.search("f.ck", ws1[0].lower()) == None and len(reg.findall("(?=(?<!\w)(\w+)(?:\W|$))", ws1[0])) < 4: # last part here is to edit out profanity in results
                        # nominees_ws.append(ws1[0])
                        nominees_ws.append(candidates[i][0])
                # if the nominee type is just person
                else:
                    if ws1 != None and not ws1[0] in nominees_ws and type(ws1[1]) != list and not isSubstring(ws1[0], nominees_ws) and reg.search("f.ck", ws1[0].lower()) == None: # last part here is to edit out profanity in results
                        # nominees_ws.append(ws1[0])
                        nominees_ws.append(candidates[i][0])

                    # if not reg_noms_person[i][0] in nominees and nom_type == ws1[1]:
                    #     nominees.append(reg_noms_person[i][0])
                
            # increment the counter keeping track of search depth
            counter2 += 1

            # base case for breaking out of loop
            if len(nominees_ws) >= max_noms or counter2 > max_search_depth:
                break

    # if the type is content
    else:
        for i in range(len(candidates)):
            # print(reg_noms[i][0])
            # print(year)

            if candidates[i][0] != None:
                if isSubstring(candidates[i][0], nominees_ws):
                    continue
                if not candidates[i][0] in ws_seen.keys():
                    ws1 = webscrape.imdb_type_check(candidates[i][0], 0)
                    # ws1 = getWSResults(candidates[i][0], year)
                    ws_seen[candidates[i][0]] = ws1
                    ws_seen = addPermutations(candidates[i][0], ws1, ws_seen)
                else:
                    ws1 = ws_seen[candidates[i][0]]
                # ws1 = webscrape.imdb_type_check(reg_noms[i][0], year)
                if ws1 != None and not ws1[0] in nominees_ws and not isSubstring(ws1[0], nominees_ws) and type(ws1[1]) == list and reg.search("f.ck", ws1[0].lower()) == None: # last part here is to edit out profanity in results
                    nominees_ws.append(ws1[0])

                    # nominees_ws.append(candidates[i][0])

                    # if not reg_noms[i][0] in nominees:
                    #     nominees.append(reg_noms[i][0])
            counter2 += 1


            # base case for breaking out of loop
            if len(nominees_ws) >= max_noms or counter2 > max_search_depth:
                break
                
    

    if winner != None and not winner.title() in nominees_ws:
        nominees_ws.append(winner.title())

    return (nominees_ws, ws_seen)


# check regexes for the times between the first quartile and third quartile of tweets announcing a winner for the award
def check_Q1_to_Q3(pandaf, rtOn: bool = False, quartiles: list = None, winner: str = "", ws_seen: Optional[dict] = None):

    year = pandaf['timestamp_ms'][pandaf.shape[0]-1].year

    nom_candidates = {}

    # if the 3rd quartile is a long time after the median, change the range to 3 minutes after the median
    if quartiles[2] > quartiles[1] + 60000000000 * 15:
        quartiles[2] = quartiles[1] + 60000000000 * 3

    # if the 1st quartile is a long time before the median, change the range to 3 minutes before the median
    if quartiles[1] > quartiles[0] + 60000000000 * 15:
        quartiles[0] = quartiles[1] - 60000000000 * 3

    for i in range(pandaf.shape[0]):
        curr_time = pandaf['timestamp_ms'][i].value

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

        

        # only check values that are after the 1st quartile (a bit before is fine) and before the median
        if(curr_time < quartiles[0] - 60000000000 * 3 or curr_time > quartiles[2]):
            # if "weaver" in curr_text.lower(): 
            #     print(curr_text)
            #     print(pd.to_datetime(quartiles[2]))
            #     print(pd.to_datetime(curr_time))
            #if i % 1000 == 0: print(i)
            continue
        
        # check times immediately after the award winner is announced (so stuff like X was robbed, should have won, etc.)
        nom_find = {}
        nom_find = getMatches(curr_text, nom_find, 2, "(['\w+\s*\-*]*)(?<![wWgG][aAoO][sStT])\s+[sS]*[RrnN][OouU][Bbs][Bb][eE][dD]", False, "bbed") # reverse
        nom_find = getMatches(curr_text, nom_find, 3, "(['\w+\s*\-*]*)\s+[sS]*[hHcC][oO][uU][lL][dD]\s*(?:[hH][aA][vV][eE]|\'*[Vv][Ee]|[aA]|[oO][fF])\s+.*\s*(?:[wW][OoIi][nN]|[gG][oO][Tt])", False, "ould") # reverse
        nom_find = getMatches(curr_text, nom_find, 4, "(['\w+\s*\-*]*)\s+(?:[jJ][uU][Ss][Tt]\s*|\s*)(?:[Ww][Aa][SszZ]|[Gg][oO][Tt])\s*(?:[Jj][Uu][Ss][Tt]\s*)*\s+[sS]*[RrnN][OouU][Bbs][Bb][eE][dD]", False, "bbed") # reverse
        nom_find = getMatches(curr_text, nom_find, 5, "(['\w+\s*\-*]*)\s+[dD][iI][dD](?:[nN]\'*[tT]|\s+[nN][oO][tT])\s+[wW][iI][nN]", False, "did") # reverse
        nom_find = getMatches(curr_text, nom_find, 21, "^(?<![Ww][Ee][Ll][Ll])(['\w+\s*\-*]*)\s+(?:[rR][eE][aA][lL][lL][yY])*\s*[Dd][Ee][Ss][Ee][Rr][Vv]", False, "deserv") # reverse
        nom_find = getMatches(curr_text, nom_find, 26, "[wW][Aa][Nn][Tt][Ee]*[Dd]*\s+(?![tT][oO])(['\w+\s*\-*]*)\s+[Tt][Oo]", False, "want") # reverse
        nom_find = getMatches(curr_text, nom_find, 27, "[sS]*[hHcC][oO][uU][lL][dD](?:\s+[hH][aA][Vv][eE]|\'[vV][eE]|a)\s+[bB][eE][eE][Nn]\s+(['\w+\s*\-*]*)", False, "ould") # not reverse
        nom_find = getMatches(curr_text, nom_find, 28, "(['\w+\s*\-*]*)\s+.*\s*(?:[nN][eE][vV][eE][rR]|[wW][oO][nN]\'*[tT])\s+[wW][iI][nN]", False, "win") # reverse
        nom_find = getMatches(curr_text, nom_find, 29, "(['\w+\s*\-*]*)\s+[dD][oO][eE][sS][nN]\'[tT]\s+(?:[wW][iI][nN]|[aA][pP][pP][rR])", False, "doesn") # reverse
        nom_find = getMatches(curr_text, nom_find, 30, "(['\w+\s*\-*]*)\s+[mM][iI][sS][sS][eE]", False, "misse") # reverse
        nom_find = getMatches(curr_text, nom_find, 31, "[gG][oO][nN][eE]\s+[tT][oO]\s+(['\w+\s*\-*]*)", False, "gone") # not reverse
        nom_find = getMatches(curr_text, nom_find, 32, "[bB][eE][tT][tT][eE][Rr]\s+[tT][hH][aA][nN]\s+(['\w+\s*\-*]*)", False, "bett") # not reverse
        nom_find = getMatches(curr_text, nom_find, 33, "[pP][oO][oO][rR]\s+(['\w+\s*\-*]*)", False, "poor") # not reverse
        nom_find = getMatches(curr_text, nom_find, 34, "[hH][oO][pP][eE][dD]\s+[tT][hH][aA][tT]\s+(['\w+\s*\-*]*)", False, "hope") # not reverse
        nom_find = getMatches(curr_text, nom_find, 35, "\s+[oO][vV][eE][rR]\s+(['\w+\s*\-*]*)", False, "over") # not reverse
        nom_find = getMatches(curr_text, nom_find, 36, "(['\w+\s*\-*]*)\s+[pP][lL][eE][aA][sS][eE]", False, "please") # reverse
        nom_find = getMatches(curr_text, nom_find, 37, "(['\w+\s*\-*]*)(?:\'[sS]|\s+[iI][sS]|\s+[wW][aA][sS])\s+[nN][oO][mM][iI][nN]", False, "nomin") # reverse
        nom_find = getMatches(curr_text, nom_find, 38, "[bB][eE][aA][tT][sS]*\s+(['\w+\s*\-*]*)", False, "beat") # not reverse
        nom_find = getMatches(curr_text, nom_find, 39, "[rR][oO][oO][tT][iI][nN][gG]\s+[fF][oO][rR]\s+(['\w+\s*\-*]*)", False, "rooting") # not reverse
        nom_find = getMatches(curr_text, nom_find, 40, "[hH][oO][pP](?:[eE]|[iI][nN][gG])\s*(?:[tT][hH][aA][tT])*(['\w+\s*\-*]*)\s+[wW][iI][nN]", False, "hop") # not reverse
        nom_find = getMatches(curr_text, nom_find, 41, "(['\w+\s*\-*]*)\s+[lL][oO][sS](?:[tT]|[eE])", False, "los") # reverse
        nom_find = getMatches(curr_text, nom_find, 42, "[pP][rR][eE][fF][eE][rR](?:[rR][eE][dD])\s+(['\w+\s*\-*]*)", False, "prefer") # not reverse
        nom_find = getMatches(curr_text, nom_find, 43, "[wW][iI][sS][hH]\s+(['\w+\s*\-*]*)\s+[wW][oOiI][nN]", False, "wish") # not reverse
        nom_find = getMatches(curr_text, nom_find, 44, "[pP][uU][lL][lL][iI][nN][gG]\s+[fF][oO][Rr]\s+(['\w+\s*\-*]*)\s+[tT][oO]\s+[wW][oOiI][nN]", False, "pull") # not reverse

        
        

        # for each regex search criteria for a nominee (ex: X should have won)
        for x in nom_find.keys():
            # if that expression was matched in the sentence, 
            if nom_find[x] != None:
                
                # print(nom_find[x].string)
                # print(nom_find[x].group(1))
                
                # add the possible permutations of the following string to the nominee candidates using doProcessing, so that one of them should be the result
                rev = True
                match x % 100:
                    case 2 | 3 | 4 | 5 | 6 | 10 | 11 | 12 | 13 | 14 | 16 | 17 | 18 | 21 | 22 | 23 | 26 | 28 | 29 | 30 | 36 | 37 | 41:
                        rev = True
                    case _: 
                        rev = False
                
                doProcessing2(nom_find[x], nom_candidates, rev)
                

    votes = {}
    # i is the # of words in the string
    for i in nom_candidates.keys():
        multiplier = 1.0
        # if a string is a single word, weigh it less (mainly accounts for person names)
        if(i == 1):
            multiplier = 0.75
        # j is an actual key-value pair of string to weighted vote
        for j in nom_candidates[i].keys():
            if(isCommon(j)):
                continue
            if (not j.title() in votes and nom_candidates[i][j]):
                votes[j.title()] = nom_candidates[i][j] * multiplier
            elif (j.title() in votes and nom_candidates[i][j]):
                votes[j.title()] += nom_candidates[i][j] * multiplier

    votes_list = []

    if(votes != {}):
        if("" in votes.keys()):
            votes[""] = 0

        # temp = max(votes, key = votes.get)
        #if temp != None: print(temp)

        votes_list = list(votes.items())
        votes_list.sort(key=(lambda x: x[1]), reverse=True)
        # print("votes ranking: " + str(votes_list))

        # ws = max(votes, key = votes.get) # webscrape.imdb_type_check(max(votes, key = votes.get), year)

    (nominees, ws_seen) =  compileNominees(votes_list, year, winner, ws_seen)
        # add that webscrape dictionary stuff in here

    return (nominees, ws_seen)


def getNominees(pandaf, winner: str, ws_seen: dict):
    if ws_seen == None: ws_seen =  {}

    qts = getQTS(pandaf, winner, False)
    return check_Q1_to_Q3(pandaf, False, qts, winner, ws_seen)

    



def main():
    # get the json twitter info
    p = os.path.dirname(os.path.realpath(__file__)) + r"\gg2013.json"

    pandaf = pd.read_json(p)

    # curr_event = events['event_nom']

    # award_names = list((list(curr_event.awards.keys())[x], x) for x in range(len(curr_event.awards.keys())))

    # award_names.sort(key=lambda x: len(x[0]), reverse=True)

    #rint(award_names)

    seen = {}
    quartiles = {}
    ws_seen = {}
    # (_, seen) = findWins(pandaf, curr_event, 4, True, 3, seen)
    # (temp, seen, qts) = findWins(pandaf, "best animated feature", 20, True, 3, seen)
    # print(temp)
    # print(temp)
    # print(findWins(pandaf, "best performance by an actor in a motion picture - drama", 0, False, 3, {})[0])

    # qts = getQTS(pandaf, "jodie foster", False)
    
    # print(list(pd.to_datetime(x) for x in qts))
    final_answer = {}
    # print(check_Q1_to_Q3(pandaf, False, qts, "jodie foster", ws_seen))

    # curr_event.awards[list(curr_event.awards.keys())[num]]
    for i in award_names:#range(len(curr_event.awards.keys())):
        print("Award #" + str(i[1]) + ": " + i[0])
        (temp, seen, _) = findWins(pandaf, list(curr_event.awards.keys())[i[1]], i[1], True, 3, seen)
        qts = getQTS(pandaf, temp, False)
        (nominees, ws_seen) = check_Q1_to_Q3(pandaf, False, qts, temp, ws_seen)
        print(nominees)
        final_answer[i[0]] = nominees

    # print(quartiles)
    print(final_answer)

if __name__ == '__main__':
    main()