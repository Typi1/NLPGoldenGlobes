import json
import os
from enum import Enum
from typing import Optional, TypedDict

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
        # alternate title names
        self.nicknames = nicknames
        # content genre or None
        self.genre = genre
        # set of ids of people who have a role in the content or empty set
        self.people = people
        # type of content (shouldn't ever be 2/person)
        self.contentType = contentType
        
    def __str__(self):
        return self.name

# class representing award
class Award:
    def __init__(self, name: str, presenter: Optional[int] = None, nomineeType: Optional[WinType] = None, nominees: Optional[set[int]] = {}, winner: Optional[int] = None):
        # award name
        self.name = name
        # id of person who is the presenter or None
        self.presenter = presenter
        # type of all nominees (picture/series/person)
        self.nomineeType = nomineeType
        # set of ids of people who are the nominees or empty set
        self.nominees = nominees
        # id of person who is the winner or None
        self.winner = winner
        

    def __str__(self):
        return self.name

# class representing award ceremony event
class Event:
    def __init__(self, name: str, host: Optional[int] = None, awards: Optional[dict] = {}, contents: Optional[dict] = {}, people: Optional[dict] = {}, name_to_id: Optional[dict] = {}):
        # event name
        self.name = name
        # id of person who is the host or None
        self.host = host
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

    def add_person(self):
        return

    # adds a person instance along with a set of nicknames. ONLY use for inputting data from parameters.json
    def add_person_init():
        return

    def add_content():
        return 

    def add_award():
        return

    def __str__(self):
        return self.name

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
    print(len(params["awards"]))
    # make an event instance to return
    for i in range(len(params["awards"])):
        print(params["awards"][i]["name"])
        print(params["awards"][i]["nominee-type"])
        print(params["awards"][i]["nominee-genre"])
        # create person or movie object here depending on nominee-type
        # to be used in adding the nominee canonical name and nicknames
        print(list(params["awards"][i]["nominees"].keys()))

    return

# compares knowledge representation scheme with ground truth and outputs what is wrong and what is missing 
def test():
    return

def main():
    parameters = load_json(os.path.dirname(os.path.realpath(__file__)) + r"\parameters.json")
    #data = load_json(os.path.dirname(os.path.realpath(__file__)) + "\\" + parameters['dataset_name'])

    #print(get_user(data[0]))
    
    input_parameters(parameters)
    return

if __name__ == "__main__":
    main()