import pandas as pd
import truecase
import re as reg
import spacy
import nltk
import webscrape


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

    year = pandaf['timestamp_ms'][pandaf.shape[0]-1].year  # the year of the event NOTE: maybe add this to the event data structure?

    for i in range(pandaf.shape[0]):

        curr_text = pandaf['text'][i]
        # curr_text = GoogleTranslator(source='auto', target='english').translate(i_text)
        curr_text = curr_text.replace("\"", "")
        curr_text = curr_text.replace("“", "")
        curr_text = curr_text.replace("”", "")
        curr_text = curr_text.replace("-", "")

        best_find1 = reg.search("\s+best", curr_text.lower()) # general one to have
        worst_find1 = reg.search("\s+worst", curr_text.lower())
        best_find2 = reg.search("b+e+a+u+t+i+f+u+l+|g+o+a+r+g+e+o+u+s+|f+a+b+u+l+o+u+s+|s+e+x+y+", curr_text.lower())
        worst_find2 = reg.search("\su+g+l+y+|h+o+r+i+b+l+e+", curr_text.lower())
        neutral_find = reg.search("\s+dress", curr_text.lower())

        if best_find1 and neutral_find:
            doProcessing(best_find1, best_dressed)
        if best_find2 and neutral_find:
            doProcessing(best_find2, best_dressed)
        if worst_find1 and neutral_find:
            doProcessing(worst_find1, worst_dressed)
        if worst_find2 and neutral_find:
            doProcessing(worst_find2, worst_dressed)
        
    if(best_dressed != {}):
        print(best_dressed)
        best = max(best_dressed, key = best_dressed.get)
        # print(best)
    if(worst_dressed != {}):
        print(worst_dressed)
        worst = max(worst_dressed, key = worst_dressed.get)
        # print(worst)
            
    return (best, worst)

def main():
    # get the json twitter info
    p = "gg2013.json"

    pandaf = pd.read_json(p)
    (best, worst) = findDressed(pandaf)
    print("Best Dressed:" + best)
    print("Worst Dressed:" + worst)

if __name__ == '__main__':
    main()
