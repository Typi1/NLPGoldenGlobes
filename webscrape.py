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

def imdb_type_check(s, year: Optional[int] = 0):
    #forming url
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

        print("name: " + str(name_txt))

        type_txt = person_html.find("p", {"class": "text-muted text-small"}).text
        type_regex = re.compile(r"[A-Z].*")

        s_type = (name_regex.search(name_txt).group(), type_regex.search(type_txt).group()[0:-2])
    
    elif content_html:
        type_txt = content_html.find("span", {"class": "genre"}).text
        name_txt = content_html.findAll("a")[1].text

        print("name: " + str(name_txt))
    
        s_type = (name_txt ,re.findall("[A-Z][a-z]*", type_txt))
    
    return s_type

def main():
    print(imdb_type_check("girls", 2013))
    
    # testerse = re.findall("\w+", "testing this word counter 920")
    # print(len(testerse))
    # for i in range(len(testerse)):
    #     res = re.search("(?:\w+\s+){" + str(i) + "}(\w+)*", "testing this word counter 920")
    #     print(res.group(1) + res.string[res.span()[1]:])
    #     print(len(testerse) - i)
    
    # test2 = re.search("^\s+([\w*\s*]*)\s+$", "  test whitespace removal ")
    # print(test2.group(1))
    # print("  test whitespace removal ".lstrip().rstrip())

    #print(str(re.search("(?:^|\s+)" + "out" + "(?:\s+|$)", "testing this out").group()).lstrip().rstrip())

    #print(re.search("win", "I win this win competition"))

    # print(["argo".lstrip().rstrip()])
    # print(re.findall("\w+", "argo"))
    # print(re.search("(?:^|\s+|-|/)" + "hey" + "(?:\s+|-|/|$)", "hey/"))
    pass

if __name__ == '__main__':
    main()