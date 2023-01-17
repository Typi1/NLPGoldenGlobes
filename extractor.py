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
    DIRECTOR = 2
    EDITOR = 3
    CINEMATOGRAPHER = 4

# class of possible genres a content can be or an award can be on
class Genre(Enum):
    COMEDY = 0
    DRAMA = 1
    DOCUMENTARY = 2
    ACTION = 3
    HORROR = 4
    ANIMATION = 5

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
    def __init__(self, name: str, genre: Optional[Genre] = None, people: Optional[set[int]] = {}):
        # content title
        self.name = name
        # content genre or None
        self.genre = genre
        # set of ids of people who have a role in the content or empty set
        self.people = people
        
    def __str__(self):
        return self.name

# class representing award
class Award:
    def __init__(self, name: str, presenter: Optional[int] = None, nominees: Optional[set[int]] = {}, winner: Optional[int] = None):
        # award name
        self.name = name
        # id of person who is the presenter or None
        self.presenter = presenter
        # set of ids of people who are the nominees or empty set
        self.nominees = nominees
        # id of person who is the winner or None
        self.winner = winner

    def __str__(self):
        return self.name

# class representing award cerimony event
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
        # dict of person id to person instance or empty dict
        self.people = people
        # mapping between person name and person id or empty dict
        self.name_to_id = name_to_id

        #id counter
        self.id_counter = 0

    def add_person(self):
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
def input_parameters():
    return

# compares knowledge representation scheme with ground truth and outputs what is wrong and what is missing 
def test():
    return

def main():
    parameters = load_json('parameters.json')
    data = load_json(parameters['dataset_name'])

    print(get_user(data[0]))
    

    return

if __name__ == "__main__":
    main()