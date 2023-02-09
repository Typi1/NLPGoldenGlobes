from bs4 import BeautifulSoup
import requests
import re
from typing import Optional

def get_soup(url_base:str, name:str):
    url = [url_base]
    name = name.replace(" ", "+")
    url.append(name)

    response = requests.get(''.join(url))

    return BeautifulSoup(response.text, "html.parser")

def imdb_type_check(s, year: Optional[int] = 0, type: Optional[int] = 0):
    #forming url
    if type == 0:
        person_soup = get_soup("https://www.imdb.com/search/name/?name=", s)
        if year != 0:
            content_soup = get_soup("https://www.imdb.com/search/title/?release_date=,"+ str(year) +"-01-01&title=", s)
        else:
            content_soup = get_soup("https://www.imdb.com/search/title/?title=", s)
        # getting html contents for person
        person_html = person_soup.find("div", {"class": "lister-item mode-detail"})
        # getting html contents for content
        content_html = content_soup.find("div", {"class": "lister-item mode-advanced"})

        s_type = None

        # added this block since les miserables wasn't working correctly since there was a barebones person entry for it for some reason.
        # this error may apply to other movies and I think(?) this should cover them but idk. - Ethan
        if person_html and content_html:
            if([s.lstrip().rstrip()] == re.findall("\w+", s)): # if there is both person and content results, and the string is ONE WORD, assume it is more likely to be a show so disregard person option
                person_html = None
            else:
                try:
                    type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
                except AttributeError:
                    person_html = None

        if person_html:
            name_txt = person_html.findAll("a")[1].text
            name_regex = re.compile(r"[A-Z].*")

            # print("name: " + str(name_txt))

            type_txt = person_html.find("p", {"class": "text-muted text-small"})
            if type_txt != None:
                type_txt = type_txt.text
                
            type_regex = re.compile(r"[A-Z].*")

            temp1 = name_regex.search(name_txt)
            temp2 = type_regex.search(type_txt)
            if temp1 == None or temp2 == None:
                s_type = None
            else:
                s_type = (temp1.group(), temp2.group()[0:-2])
        
        elif content_html:
            temp = content_html.find("span", {"class": "genre"})
            if temp != None:
                type_txt = temp.text
            else:
                type_txt = ""
            name_txt = content_html.findAll("a")[1].text

            # print("name: " + str(name_txt))
        
            s_type = (name_txt ,re.findall("[A-Z][a-z]*", type_txt))
        
        return s_type
    elif type == 1:
        #forming url
        person_soup = get_soup("https://www.imdb.com/search/name/?name=", s)
        
        # getting html contents for person
        person_html = person_soup.find("div", {"class": "lister-item mode-detail"})

        s_type = None
        try:
            type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
        except AttributeError:
            person_html = None

        if person_html:
            name_txt = person_html.findAll("a")[1].text
            name_regex = re.compile(r"[A-Z].*")

            # print("name: " + str(name_txt))

            type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
            type_regex = re.compile(r"[A-Z].*")

            s_type = (name_regex.search(name_txt).group(), type_regex.search(type_txt).group()[0:-2])

        return s_type
    elif type == 2:
        if year != 0:
            content_soup = get_soup("https://www.imdb.com/search/title/?release_date=,"+ str(year) +"-01-01&title=", s)
        else:
            content_soup = get_soup("https://www.imdb.com/search/title/?title=", s)
        # getting html contents for content
        content_html = content_soup.find("div", {"class": "lister-item mode-advanced"})
        s_type = None
        try:
            type_txt = content_html.find("span", {"class": "genre"}).text
        except AttributeError:
            content_html = None
        if content_html:
            type_txt = content_html.find("span", {"class": "genre"}).text
            name_txt = content_html.findAll("a")[1].text

        # print("name: " + str(name_txt))
    
            s_type = (name_txt ,re.findall("[A-Z][a-z]*", type_txt))
        
        return s_type

def imdb_person_check(s, year: Optional[int] = 0):
    #forming url
    person_soup = get_soup("https://www.imdb.com/search/name/?name=", s)
    
    # getting html contents for person
    person_html = person_soup.find("div", {"class": "lister-item mode-detail"})

    s_type = None
    try:
        type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
    except AttributeError:
        person_html = None

    if person_html:
        name_txt = person_html.findAll("a")[1].text
        name_regex = re.compile(r"[A-Z].*")

        # print("name: " + str(name_txt))

        type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
        type_regex = re.compile(r"[A-Z].*")

        s_type = (name_regex.search(name_txt).group(), type_regex.search(type_txt).group()[0:-2])

    return s_type