import json
import os
from enum import Enum
from typing import Optional, TypedDict, Union
import re as reg

# HELPER FUNCTIONS FOR LOADING/FORMATING THE DATA

def load_json(filename):
    path = os.path.join(os.getcwd(), filename)
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def get_text(tw):
    return tw['text']

def get_user(tw):
    return tw['user']['screen_name']

def get_user_id(tw):
    return tw['user']['id']

def get_tw_id(tw):
    return tw['id']

def get_time(tw):
    return tw['timestamp_ms']


# CLASSES FOR KNOWLEDGE REPRESENTATION

# class of possible roles a person could have in a content 
class Role(Enum):
    LEADING = 0
    ACTOR = 1
    ACTRESS = 2
    DIRECTOR = 3
    EDITOR = 4
    CINEMATOGRAPHER = 5
    SCREENWRITER = 6
    MUSICIAN = 7

# class of possible genres a content can be or an award can be on
class Genre(Enum):
    COMEDY = 0
    DRAMA = 1
    DOCUMENTARY = 2
    ACTION = 3
    HORROR = 4
    ANIMATION = 5
    MUSICAL = 6

# class to distinguish between the different types of winners
class WinType(Enum):
    PICTURE = 0
    SERIES = 1
    PERSON = 2
    OTHER = 3

# class representing people   
class Person:
    def __init__(self, id: int, name: str, nicknames: Optional[set[str]] = {}, role: Optional[Role] = None, content_in: Optional[str] = None):
        # person id
        self.id = id
        # person name
        self.name = name
        # set of possible other names for person or empty set
        self.nicknames = nicknames
        # role of person or None
        self.role = role
        # name of the content the person had a role in or None
        self.content_in = content_in

    def __str__(self):
        return self.name

# class representing content, like movies or tv shows
class Content:
    def __init__(self, name: str, nicknames: Optional[set[str]] = {}, genre: Optional[Genre] = None, people: Optional[set[int]] = {}, contentType: Optional[WinType] = None):
        # content title
        self.name = name
        # alternate title names or empty set
        self.nicknames = nicknames
        # content genre or None
        self.genre = genre
        # set of ids of people who have a role in the content or empty set
        self.people = people
        # type of content (shouldn't ever be 2/person) or None
        self.contentType = contentType
        
    def __str__(self):
        return self.name

# class representing award
class Award:
    def __init__(self, name: str, nicknames: Optional[set[str]] = {}, presenters: Optional[set[int]] = None, nomineeType: Optional[WinType] = None, nominees: Optional[Union[set[int], set[str]]] = {}, winner: Optional[Union[int, str]] = None):
        # award name
        self.name = name
        # alternate names for the award or empty set
        self.nicknames = nicknames
        # ids of people who are the presenters or None
        self.presenters = presenters
        # type of all nominees (picture/series/person) or None
        self.nomineeType = nomineeType
        # set of ids of people or content names (keys) who are the nominees or empty set
        self.nominees = nominees
        # id of person or name of content (key) who is the winner or None
        self.winner = winner
        

    def __str__(self):
        return self.name

# class representing award ceremony event
class Event:
    def __init__(self, name: Optional[str] = None, hosts: Optional[dict] = {}, awards: Optional[dict] = {}, contents: Optional[dict] = {}, people: Optional[dict] = {}, name_to_id: Optional[dict] = {}):
        # event name
        self.name = name
        # dict of ids of people who are the host to the corresp. person instance or None
        self.hosts = hosts
        # dict of award name to award instance or empty dict
        self.awards = awards
        # dict of content name to content instance or empty dict
        self.contents = contents
        # dict of PERSON ID to person instance or empty dict
        self.people = people
        # mapping between person NAME and PERSON ID or empty dict
        self.name_to_id = name_to_id

        #id counter
        self.id_counter = 0


    # only use for adding people from given answers data, not for when doing other stuff later
    # returns id used by person created
    def add_person_init(self, psn: str, is_hst: bool):
        # we should probably improve the immediately proceeding check since name_to_id is intended to be able to create separate ids for diff people with similar names
        # if the name given is new, create a new id and increment ID counter, then create a person instance
        if(not (psn in self.name_to_id)):
            self.name_to_id[psn] = self.id_counter
            self.people[self.id_counter] = Person(self.id_counter, psn, None, None, None)
            self.id_counter += 1

        # if the person is a host and they are not already in the host dictionary, add them
        if(is_hst and not (psn in self.hosts)):
            self.hosts[self.name_to_id[psn]] = self.people[self.name_to_id[psn]]

        return

    # only use for adding content from given answers data, not for when doing other stuff later
    def add_content_init(self, con: str, typ: Optional[WinType] = None):
        if(not (con in self.contents)):
            self.contents[con] = Content(con, None, None, None, typ)

        return

    # only use for adding awards from given answers data, not for when doing other stuff later
    # add people/content in the award first!!!
    def add_award_init(self, awa: str, presenters: Optional[set[int]] = None, typ: Optional[WinType] = None, nominees: Optional[Union[set[int], set[str]]] = {}, winner: Optional[Union[int, str]] = None):
        if(not (awa in self.awards)):
            # convert list of presenter names to a list of corresp. ids
            if(presenters != None):
                presenters = list(self.name_to_id[x] for x in presenters)

            if(typ == WinType.PERSON):
                if(nominees != None and nominees != {}):
                    nominees = list(self.name_to_id[x] for x in nominees)
                    nominees.append(self.name_to_id[winner])
                if(winner != None):
                    winner = self.name_to_id[winner]
            elif(nominees != None and nominees != {}):
                nominees.append(winner)
                
            
            self.awards[awa] = Award(awa, None, presenters, typ, nominees, winner)

        return

    def add_person(self):
        return

    def add_content(self):
        return 

    def add_award(self):
        return

    def __str__(self):

        peop = ""
        for x in self.people:
            peop += str(self.people[x]) + "\n\t\t"

        cont = ""
        for x in self.contents:
            cont += str(self.contents[x].contentType) + ": " + str(self.contents[x]) + "\n\t\t  "

        awar = ""
        for x in self.awards:
            wnr = ""
            if(self.awards[x].nomineeType == WinType.PERSON):
                wnr = str(self.people[self.awards[x].winner])
            else:
                wnr = self.awards[x].winner

            noms = ""
            for y in self.awards[x].nominees:
                if(self.awards[x].nomineeType == WinType.PERSON):
                    noms += str(self.people[y]) + "\n\t\t\t\t  "
                else:
                    noms += str(y) + "\n\t\t\t\t  "
            noms = noms[:-7]

            awar += str(self.awards[x]) + "\n\t\t\tnominees: " + noms + "\n\t\t\twinner: " + wnr + "\n\n\t\t" 

        return  "event_name: " + self.name + "\n\t" + \
                "hosts: " + str(list(str(self.people[x]) for x in self.hosts)) + "\n\t" + \
                "people: " + peop + "\n\t" + \
                "contents: " + cont + "\n\t" + \
                "awards: " + awar

# FUNCTIONS TO COMPLETE THE TASKS
"""
Tasks:
1. winners, given nominees and award names X
2. winners, given only award names X
3. nominees, given award names X
4. award names (given only name of the award ceremony) X
5. award presenter(s), given award names X
6. host(s) (given name of award ceremony) X
"""
def find_winners():
    return

def find_nominees():
    return

def find_awards():
    return

def find_award_host():
    return

def find_event_host():
    return

# gets the information from parameters.json and formats it into our knowledge representation scheme
def input_parameters(params):
    #print(len(params["award_data"]))
    #print(list(params["award_data"].keys()))

    # make multiple event instances for different parts of our tests
    events = {
        'event_key': Event("Golden Globes 2013"), # has all the data on hosts, awards, presenters, nominees, winners
        'event_nom': Event("Golden Globes 2013"), # has data on hosts, awards, presenters, nominees
        'event_pre': Event("Golden Globes 2013"), # has data on hosts, awards, presenters
        'event_awa': Event("Golden Globes 2013"), # has data on hosts, awards
        'event_hos': Event("Golden Globes 2013"), # has data on hosts
        'event_nul': Event() # no data
    }

    # add host data/person instances
    for i in list(events.keys())[:-1]:
        for h in params["hosts"]:
            events[i].add_person_init(h, True)

    for i in list(params["award_data"].keys()):
        # print(i) # award name
        # print(params["award_data"][i]["nominees"]) # list of award nominees
        # print(params["award_data"][i]["presenters"]) # list of presenters for the award
        # print(params["award_data"][i]["winner"]) # winner of award
        # NOTE: in the gg2013answers.json, the winner isn't included in the list of nominees so we should adopt this convention for our results file

        wt = None
        # first determine whether the award is given to content or a person (find the WinType of the nominees and winner)
        if( reg.search("director", i) != None
            or reg.search("actor", i) != None
            or reg.search("actress", i) != None
            or reg.search("demille", i) != None): # if any of these searches come back with a result, we know the WINTYPE is person
            wt = WinType.PERSON
        elif(reg.search("series", i) != None): # if this search comes back with a result, we know the WINTYPE is series
            wt = WinType.SERIES
        else: # otherwise, WINTYPE is picture
            wt = WinType.PICTURE

        # add presenters as people
        for j in list(events.keys())[:-3]:
            for pres in params["award_data"][i]["presenters"]:
                events[j].add_person_init(pres, False)

        # add nominees/winners as either content or people depending on the value of wt
        if(wt == WinType.PERSON):
            for j in list(events.keys())[:-4]:
                for nom in params["award_data"][i]["nominees"]:
                    events[j].add_person_init(nom, False)
                events[j].add_person_init(params["award_data"][i]["winner"], False) # adds the winner so that it is included in the nominees
        elif(wt == WinType.PICTURE or wt == WinType.SERIES):
            for j in list(events.keys())[:-4]:
                for nom in params["award_data"][i]["nominees"]:
                    events[j].add_content_init(nom, wt)
                events[j].add_content_init(params["award_data"][i]["winner"], wt)

        events['event_key'].add_award_init(i, params["award_data"][i]["presenters"], wt, params["award_data"][i]["nominees"], params["award_data"][i]["winner"])
        
        events['event_nom'].add_award_init(i, params["award_data"][i]["presenters"], wt, params["award_data"][i]["nominees"])

        events['event_pre'].add_award_init(i, params["award_data"][i]["presenters"])

        events['event_awa'].add_award_init(i)

    return events

# compares knowledge representation scheme with ground truth and outputs what is wrong and what is missing 
def test():
    return

def main():
    parameters = load_json(os.path.dirname(os.path.realpath(__file__)) + r"\gg2013answers.json")
    #data = load_json(os.path.dirname(os.path.realpath(__file__)) + "\\" + parameters['dataset_name'])

    #print(get_user(data[0]))
    
    events = input_parameters(parameters)

    print(events['event_key'])

    return

if __name__ == "__main__":
    main()