from collections import Counter
import re
import json 
import os

# made by Gustavo
def load_json(filename):
    path = os.path.join(os.getcwd(), filename)
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def findAwa(tweets):

# loading the data
    data = load_json(tweets)

    # data without retweets
    data_no_rt = []
    for tw in data:
        text = tw["text"]

        if not re.search("^RT\s", text):
            data_no_rt.append(tw)

    # getting the tweets that start with "Best" and continue on with another word with a capital letter
    has_best = []
    for tw in data_no_rt:
        text = tw["text"]

        if re.search("^Best\s[A-Z].+", text):
            has_best.append(text)

    awards_d = Counter(has_best)
    # print(len(awards_d.keys()))
    # data without retweets

    # print(len(awards_d.keys()))

    ## further filtering idea by grabbing relevant sentence structure
    a_lst = []
    for k in awards_d.keys():
        goes_to = re.search("[gG]oes [Tt]o",k)
        if goes_to:
            a_lst.append(k[:goes_to.start()].strip())

        colon = re.search(":\s",k)
        if colon:
            a_lst.append(k[:colon.start()].strip())

        dash = re.search("^Best\s[A-Z].+\s-",k)
        if dash:
            a_lst.append(k[:dash.end()-2].strip())

    awards_d = Counter(a_lst)
    # print(len(awards_d.keys()))

    # deleting tweets which fit one of a given set of heuristics that I found to be a good way to filter out tweets
    del_lst = []
    for k, v in awards_d.items():
        sen = k.split(" ")
        bools = (len(sen) > 9) or re.search("[^\w\s]", k) #or (v<2) # or (':' in k) or (',' in k) or ('-' in k)
        if bools: del_lst.append(k)
    for k in del_lst:
        del awards_d[k]

    # print(len(awards_d.keys()))

    # deleting all tweets that only show up once if they don't have the words present in the tweets that show up more than once
    words_set = set()
    for k, v in awards_d.items():
        if v > 1: 
            k = k.split(" ")
            for w in k:
                words_set.add(w)

    del_lst = []
    for k, v in awards_d.items():
        sen = k.split(" ")
        if v == 1:
            for w in sen:
                if w not in words_set:
                    del_lst.append(k)
                    break
    for k in del_lst:
        del awards_d[k]

    # print(len(awards_d.keys()))

    # replace words with synonyms to create more explicit duplicates which are then removed
    new_awards_d = Counter()
    for k, v in awards_d.items():
        k = k.replace("TV Series", "Television")
        k = k.replace("Television Series", "Television")
        k = k.replace(" TV ", " Television ")
        k = k.replace(" TV", " Television")

        k = k.replace(" Movie ", " Motion Picture ")
        k = k.replace(" Movie", " Motion Picture")

        k = k.replace("Mini Series", "Miniseries")
        k = k.replace("Mini series", "Miniseries")
        k = k.replace("mini series", "Miniseries")

        k = k.replace("Foreign Film", "Foreign Language Film")
        k = k.replace( "Feature Film", "Film")

        k = k.replace("Performance by an", "")
        k = k.replace("  ", " ")
        
        new_awards_d[k] += v

    awards_d = new_awards_d
    # print(len(awards_d.keys()))

    # removing duplicates which only differ by spaces, symbols, or different wording
    awards_set = Counter()
    awards_d_to_s = {}
    for k, v in awards_d.items():
        clean_k = k.replace("in a", "")
        clean_k = clean_k.replace("for", "")
        clean_k = clean_k.replace("Made", "")
        clean_k = clean_k.replace("or", "")

        clean_k = clean_k.replace("Feature Film", "Picture")
        clean_k = clean_k.replace("Feature", "Picture")
        clean_k = clean_k.replace("Original", "")
        clean_k = clean_k.replace("Musical", "")
        clean_k = clean_k.replace("Series", "")
        
        clean_k = clean_k.replace("Motion Picture", "Picture")
        clean_k = clean_k.replace("Film", "Picture")
        clean_k = clean_k.replace("Comedy or Musical", "Comedy")
        clean_k = clean_k.replace(" ", "")

        txt_lst = re.split("/W", clean_k)
        txt_lst = [*" ".join(txt_lst).strip()]
        txt_lst.sort()
        txt = "".join(txt_lst)

        awards_d_to_s[k] = txt
        awards_set[txt] += v

    seen = set()
    new_awards_d = Counter()
    for k, v in awards_d.items():
        txt = awards_d_to_s[k]
        if txt not in seen:
            seen.add(txt)
            new_awards_d[k] = awards_set[txt]

    awards_d = new_awards_d
    # print(len(awards_d.keys()))

    # deleting more duplicates
    del_set = set()
    for k in awards_d.keys():
        k_lst = k.split(" ")
        for k2 in awards_d.keys():
            k2_lst = k2.split(" ")

            if len(k_lst) >= len(k2_lst):
                continue
            elif k_lst == k2_lst[:len(k_lst)]:
                del_set.add(k)
    for d in del_set:
        del awards_d[d]

    # print(len(awards_d.keys()))

    # deleting awards that have "in a" but no "Motion Picture / Television / Miniseries"
    del_lst = []
    for k, v in awards_d.items():
        if "in a" in k:
            if not ("Motion Picture" in k or "Television" in k or "Miniseries" in k):
                del_lst.append(k)
    for k in del_lst:
        del awards_d[k]

    # print(len(awards_d.keys()))

    # printing list of awards
    awards_lst = list(awards_d.keys())
    # for a in awards_lst:
    #     print(a)

    return awards_lst