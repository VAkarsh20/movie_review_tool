import wikipedia
import requests
from bs4 import BeautifulSoup
import re

def get_wiki_info():
    
    # Parse Wikipedia
    tries = 3
    while tries > 0:
        try:
            title = input("What is the film title?\n")
            wiki_title = title.replace(" ", "_")
            imdb_id = get_imdb_id(wiki_title)
            infobox = parse_wiki("https://en.wikipedia.org/wiki/" + wiki_title)

            # Change the film title if it has a (film) tag end the end of the wikipedia search
            if title.endswith("film)"):
                title = title[:title.rfind(' (')]
            tries = 0            
            return title, imdb_id, infobox
        except:
            tries -= 1
            print("Film not found. Please try again.")
    print("Unable to find movie. Please restart app.")
    return None, None, None

# TODO: Replace this function with a better way to get imdb id (somethings returns two different)
def get_imdb_id(film):
    
    links = " ".join(wikipedia.WikipediaPage(title=film).references)
    imdb_id = set(re.findall(pattern = "tt[0-9]+", string=links))
    # imdb_id = [x.replace("https://www.imdb.com/title/","").partition("/")[0] for x in links if("https://www.imdb.com/title/" in x)]

    # if len(imdb_id) > 1 and len(set(imdb_id)) > 1:
    if len(imdb_id) > 1:
        return input("There are two imdb ids: {}. Please input imdb id for {}.\n".format(imdb_id, film))

    return imdb_id.pop()

# Taken from https://www.geeksforgeeks.org/web-scraping-from-wikipedia-using-python-a-complete-guide/
def parse_wiki(url):
    
    # get URL
    page = requests.get(url)
    
    # scrape webpage
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # create object from infobox
    object = soup.find(class_="infobox vevent")
    
    # find all the tags that are keys and values
    keys = object.find_all(class_="infobox-label")
    vals = object.find_all(class_="infobox-data")
    
    # Find all the key value pairs 
    infobox = {}
    for i in range(len(keys)):
        key = keys[i].get_text().strip()
        val = vals[i].get_text().strip().split("\n")
        infobox[key] = val
    
    return infobox