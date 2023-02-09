import os
import numpy as np
import pandas as pd
import re as reg
import webscrape
import json

import findAwards
import findNominees
import findWinners
import findDressed
import findPresenters
import findHosts

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here

    json_in = None
    with open('results.json', 'r') as of:
        json_in = json.load(of)

    hosts = json_in["Hosts"]

    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here

    json_in = None
    with open('results.json', 'r') as of:
        json_in = json.load(of)

    awards = json_in["Awards"]

    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here

    json_in = None
    with open('results.json', 'r') as of:
        json_in = json.load(of)

    nominees = {}

    for award in json_in.keys():
        if award == "Hosts" or award == "Awards":
            continue
        nominees[award] = json_in[award]["Nominees"]

    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here

    json_in = None
    with open('results.json', 'r') as of:
        json_in = json.load(of)

    winners = {}

    for award in json_in.keys():
        if award == "Hosts" or award == "Awards":
            continue
        winners[award] = json_in[award]["Winner"]

    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here

    json_in = None
    with open('results.json', 'r') as of:
        json_in = json.load(of)

    presenters = {}

    for award in json_in.keys():
        if award == "Hosts" or award == "Awards":
            continue
        presenters[award] = json_in[award]["Presenters"]

    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here

    
    

    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''

    # This should be in a human-readable format like what is on Canvas example

    # Your code here

    # read the dataset
    p = "gg2013.json"
    pandaf = pd.read_json(p)
    # print(pandaf)
    hosts = findHosts.findHosts(pandaf)
    dress = findDressed.findDressed(pandaf)

    awards = findAwards.findAwa(p)

    # print(awards)
    

    win_seen = {}
    list_seen = {}
    ws_seen = {}
    nom_seen = {}
    pres_seen = {}

    winners = {}
    nominees = {}
    presenters = {}

    sorted_awards = OFFICIAL_AWARDS_1315

    sorted_awards.sort(key=lambda x: len(x), reverse=True)

    # print(sorted_awards)

    large_input = {"Hosts": hosts, "Awards": awards}

    for award_off in sorted_awards:
        (temp_win, win_seen) = findWinners.findWins(pandaf, award_off, 0, True, 3, win_seen)
        winners[award_off] = temp_win.title()
        # print(temp_win)
        (temp_nom, ws_seen) = findNominees.getNominees(pandaf, temp_win, ws_seen, award_off)
        nominees[award_off] = temp_nom
        temp_pres = findPresenters.findPres(pandaf, award_off, 3)
        temp_temp_pres = []
        for ii in temp_pres:
            temp_temp_pres.append(ii)
        presenters[award_off] = temp_temp_pres
        large_input[award_off] = {"Presenters": temp_pres, "Nominees": temp_nom, "Winner": temp_win.title()}

    # print(hosts)
    # print(awards) 
    # print(presenters)
    # print(nominees)
    # print(winners)
    # print(ws_seen)

    jsonF = json.dumps(large_input, indent=4)

    with open("results.json", "w") as of:
        of.write(jsonF)


    # human readable output: 
    print("Hosts: ")
    for ii in hosts:
        print("\t"+ii)

    print("User-found awards: ")
    for ii in awards:
        print("\t" + ii)

    for ii in sorted_awards:
        print("\nAward: " + ii)
        print("\tPresenters: ")
        for jj in presenters[ii]:
            print("\t\t"+jj)
        print("\tNominees: ")
        for jj in nominees[ii]:
            print("\t\t"+jj)
        print("\tWinner: " + winners[ii])

    print("\nBest Dressed: ")
    print("\t"+dress[0])
    print("Worst Dressed: ")
    print("\t"+dress[1])

    return

if __name__ == '__main__':
    pre_ceremony()
    main()