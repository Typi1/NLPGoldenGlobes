import pandas as pd
import truecase
import re as reg
import spacy
import nltk

# made by Sean and Gustavo

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def doProcessing(s, dress_candidates):
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
                if ent.text in dress_candidates:
                    dress_candidates[ent.text] += 1
                else:
                    dress_candidates[ent.text] = 1
    return


def findDressed(pandaf):

    best_dressed = {}
    worst_dressed = {}

    for i in range(pandaf.shape[0]):

        curr_text = pandaf['text'][i]
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", "")
        curr_text = curr_text.replace("”", "")
        curr_text = curr_text.replace("-", "")
        curr_text = curr_text.lower()
        best_find1 = reg.search("\s+best", curr_text) # general one to have
        worst_find1 = reg.search("\s+worst", curr_text)
        best_find2 = reg.search("b+e+a+u+t+i+f+u+l+|g+o+a+r+g+e+o+u+s+|f+a+b+u+l+o+u+s+|s+e+x+y+", curr_text)
        worst_find2 = reg.search("\su+g+l+y+|h+o+r+i+b+l+e+", curr_text)
        neutral_find = reg.search("\s+dress", curr_text)

        if best_find1 and neutral_find:
            doProcessing(best_find1, best_dressed)
        if best_find2 and neutral_find:
            doProcessing(best_find2, best_dressed)
        if worst_find1 and neutral_find:
            doProcessing(worst_find1, worst_dressed)
        if worst_find2 and neutral_find:
            doProcessing(worst_find2, worst_dressed)
        
    if(best_dressed != {}):
        # print(best_dressed)
        best = max(best_dressed, key = best_dressed.get)
        # print(best)
    if(worst_dressed != {}):
        # print(worst_dressed)
        worst = max(worst_dressed, key = worst_dressed.get)
        # print(worst)
            
    return (best, worst)