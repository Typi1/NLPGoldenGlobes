from bs4 import BeautifulSoup
import requests
import re

def get_soup(url_base:str, name:str):
    url = [url_base]
    name = name.replace(" ", "+")
    url.append(name)

    response = requests.get(''.join(url))

    return BeautifulSoup(response.text, "html.parser")

def imdb_type_check(s):
    #forming url
    person_soup = get_soup("https://www.imdb.com/search/name/?name=", s)
    content_soup = get_soup("https://www.imdb.com/search/title/?title=", s)
    # getting html contents for person
    person_html = person_soup.find("div", {"class": "lister-item mode-detail"})
    # getting html contents for content
    content_html = content_soup.find("div", {"class": "lister-item mode-advanced"})

    s_type = None
    if person_html:
        name_txt = person_html.findAll("a")[1].text
        name_regex = re.compile(r"[A-Z].*")

        type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
        type_regex = re.compile(r"[A-Z].*")

        s_type = (name_regex.search(name_txt).group(), type_regex.search(type_txt).group()[0:-2])
    
    elif content_html:
        type_txt = content_html.find("span", {"class": "genre"}).text
        name_txt = content_html.findAll("a")[1].text
    
        s_type = (name_txt ,re.findall("[A-Z][a-z]*", type_txt))
    
    return s_type