import movie_pb2
import string
import requests
from bs4 import BeautifulSoup
import requests
import sys
from google.protobuf import text_format
from sheets import initialize_to_sheets, post_to_sheets
from datetime import datetime
from letterboxd import post_to_letterboxd
from imdb import post_to_imdb
import os
import wikipedia
import pandas as pd
from csv import writer
import multiprocessing as mp
import subprocess
import re
import copy
from utils.proto_utils import *
from utils.print_utils import *

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


def get_field(infobox, key):
    
    # Check to see if the key is valid
    if key not in infobox:
        return None

    # Get all the people for the field
    person_list = []
    for name in infobox[key]:
        person = movie_pb2.Movie.Review.Person()
        person.name = name
        person_list.append(person)
    
    # Initialize the field
    if key == "Directed by":
        direction = movie_pb2.Movie.Review.Direction()
        direction.director.extend(person_list)
        direction.rating = "TODO"
        direction.comments = "Direction (macroscale is; microscale is; direction of actors is; storytelling is; tension is)"
        return direction
    elif key == "Music by":
        score = movie_pb2.Movie.Review.Score()
        score.composer.extend(person_list)
        score.rating = "TODO"
        score.comments = "Score ()"
        return score
    elif key == "Cinematography":
        cinematography = movie_pb2.Movie.Review.Cinematography()
        cinematography.cinematographer.extend(person_list)
        cinematography.rating = "TODO"
        cinematography.comments = "Cinematography ()"
        return cinematography
    elif key == "Edited by":
        editing = movie_pb2.Movie.Review.Editing()
        editing.editor.extend(person_list)
        editing.rating = "TODO"
        editing.comments = "Editing ()"
        return editing

    return None  

def get_generic(category):
    # Create generic object
    return movie_pb2.Movie.Review.GenericCategory(rating="TODO", comments = "{} ()".format(category))

def get_acting(infobox):
    
    # Create acting object
    acting = movie_pb2.Movie.Review.Acting()

    # Parse all of the possible actors (with their comments) and append them to the object
    for name in infobox["Starring"]:
        performance = movie_pb2.Movie.Review.Acting.Performance(actor = movie_pb2.Movie.Review.Person(name = name))
        performance.rating = "TODO"
        performance.comments = "from " + name + " ()"
        acting.performance.append(performance)

    # Add comments on the overall cast
    acting.cast.CopyFrom(get_generic("from the rest of the cast ()"))

    # Overall Comments on Acting
    acting.comments = ""

    return acting


def get_writing(infobox):
    
    # Create writing object
    story = movie_pb2.Movie.Review.Story()
    screenplay = movie_pb2.Movie.Review.Screenplay()

    # Check to see if the writers wrote both the story and the screenplay
    if "Written by" in infobox:
        for name in infobox["Written by"]:
            writer = movie_pb2.Movie.Review.Person()
            writer.name = name
            story.writer.append(writer)
            screenplay.writer.append(writer)
    elif "Story by" in infobox and "Screenplay by" in infobox:
        for name in infobox["Story by"]:
            writer = movie_pb2.Movie.Review.Person()
            writer.name = name
            story.writer.append(writer)

        for name in infobox["Screenplay by"]:
            writer = movie_pb2.Movie.Review.Person()
            writer.name = name
            screenplay.writer.append(writer)
    elif "Screenplay by" in infobox:
        for name in infobox["Screenplay by"]:
            writer = movie_pb2.Movie.Review.Person()
            writer.name = name
            story.writer.append(writer)
            screenplay.writer.append(writer)
    else:
        story = None
        screenplay = None

    # Add comments for the writing
    if story != None and screenplay != None:
        story.rating = "TODO"
        story.comments = "Story (The concept is; the plot structure is; flow between sequences is; character writing is)"
        screenplay.rating = "TODO"
        screenplay.comments = "Screenplay (The dialogue is; the humor is; the symbolism is; the foreshadowing is)"

    return story, screenplay


def find_release_year(infobox):
    
    # Find the release year for the movie
    release_key = "Release dates" if "Release dates" in infobox else "Release date"
    release_year = infobox[release_key][0]
    return int(release_year.split('\xa0')[2]) if '\xa0' in release_year else int(release_year.partition(", ")[-1].partition(" ")[0])

def find_review_date():
    
    # Set the review date
    today = datetime.now()
    return "{}/{}/{}".format(today.strftime('%m'), today.strftime('%d'), today.strftime('%Y')) 


def set_id(imdb_id=None, redux=False):
    if redux:
        df = pd.read_csv("movies.csv")
        return int(df[df["imdbID"] == imdb_id]["Id"])
    else:
        return len(os.listdir('movies_textproto/'))


def create_proto(redux=False):
    
    # Find some of the fields and infobox
    title, imdb_id, infobox = get_wiki_info()
    if title == None:
        return

    story, screenplay = get_writing(infobox)

    # Creating the review object
    review = movie_pb2.Movie.Review(
        direction = get_field(infobox, "Directed by"), # parse_direction(infobox), 
        acting = get_acting(infobox),
        story=story,
        screenplay=screenplay,
        score = get_field(infobox, "Music by"), # parse_score(infobox),
        cinematography = get_field(infobox, "Cinematography"), # parse_cinematography(infobox),
        editing = get_field(infobox, "Edited by"), # parse_editing(infobox),
        sound = get_generic(category="Sound"), # "Sound ()",
        visual_effects = get_generic(category="Visual Effects"), # "Visual Effects ()",
        production_design = get_generic(category="Production Design"), # "Production Design ()",
        makeup = get_generic(category="Makeup"), # "Makeup ()",
        costumes = get_generic(category="Costumes"), # "Costumes ()",
        pacing = "Pacing ",
        climax = "Climax ",
        tone = "Tone ",
        final_notes = "",
        overall = "Overall, "
    )

    # creating the review object from the fields already initialized
    return movie_pb2.Movie(title=title, rating=0.1, review=review, release_year = find_release_year(infobox), review_date = find_review_date(), redux=redux, id=set_id(imdb_id, redux), imdb_id=imdb_id)


def create_proto_free(redux=False):
    title, imdb_id, infobox = get_wiki_info()
    return movie_pb2.MovieFree(title=title, rating=0.1, review="", release_year = find_release_year(infobox), review_date = find_review_date(), redux=redux, id=set_id(imdb_id, redux), imdb_id=imdb_id)

# TODO: Redux is not created for Home Alone 2
def move_redux_reviews(filename):
    path = os.path.join(os.path.dirname(__file__), 'movies_textproto/')
    count = 0
    while os.path.exists(path + ("reduxed/" * count) + filename + ".textproto"):
        count += 1

    if not os.path.exists(path + ("reduxed/" * count)):
        os.mkdir(path + ("reduxed/" * count))

    while count > 0:
        os.rename(path + ("reduxed/" * (count - 1)) + filename + ".textproto", path + ("reduxed/" * (count)) + filename + ".textproto")
        count -= 1

def reviews_sorted():

    # Getting all the Titles and Ratings
    df = pd.read_csv("movies.csv")[["Title", "Rating"]]

    # Sortings in descending order and returning as a string
    df = df.sort_values(by=['Rating'], ascending=False)
    return df.to_string(index=False)

def sanity_check(proto):
    if isinstance(proto, movie_pb2.MovieFree):
        if proto.review == "":
            raise ValueError("Free format needs to have text")
        return

    # Checking if tiers are finished
    if proto.review.direction.rating == "TODO":
        raise ValueError("Direction needs to be given a tier")
    acting = proto.review.acting
    for performance in proto.review.acting.performance:
        if performance.rating == "TODO":
            raise ValueError("{} needs to be given a tier".format(performance.actor.name))
    if acting.cast.rating == "TODO":
        raise ValueError("Acting cast needs to be given a tier")
    if proto.review.story.rating == "TODO":
        raise ValueError("Story needs to be given a tier")
    if proto.review.screenplay.rating == "TODO":
        raise ValueError("Screenplay needs to be given a tier")
    if proto.review.score.rating == "TODO":
        raise ValueError("Score needs to be given a tier")
    if proto.review.cinematography.rating == "TODO":
        raise ValueError("Cinematography needs to be given a tier")
    if proto.review.editing.rating == "TODO":
        raise ValueError("Editing needs to be given a tier")
    if proto.review.sound.rating == "TODO":
        raise ValueError("Sound needs to be given a tier")
    if proto.review.production_design.rating == "TODO":
        raise ValueError("Production Design needs to be given a tier")
    if proto.review.makeup.rating == "TODO":
        raise ValueError("Makeup needs to be given a tier")
    if proto.review.costumes.rating == "TODO":
        raise ValueError("Costumes needs to be given a tier")
    
    # Checking if notes are complete
    if proto.review.pacing == "Pacing ":
        raise ValueError("Pacing notes are incomplete")
    if proto.review.climax == "Climax ":
        raise ValueError("Climax notes are incomplete")
    if proto.review.climax == "Tone ":
        raise ValueError("Tone notes are incomplete")
    if proto.review.overall == ("Overall, "):
        raise ValueError("Overall notes are incomplete")


if __name__=="__main__":
    
    argc = len(sys.argv)

    # Reset clock
    subprocess.run(["sudo", "hwclock", "-s"])

    if argc == 1 or sys.argv[1] == "create_proto":
        # TODO: Deletes original version of the file
        if argc > 2 and sys.argv[2] == "redux":
            movie = create_proto(True)
            move_redux_reviews("{} ({})".format(movie.title, movie.release_year))
        else:
            movie = create_proto()
            initialize_to_sheets(movie)
        write_proto(movie)
    
    elif sys.argv[1] == "create_proto_free":
        # TODO: Deletes original version of the file
        if argc > 2 and sys.argv[2] == "redux":
            movie = create_proto(True)
            move_redux_reviews("{} ({})".format(movie.title, movie.release_year))
            initialize_to_sheets(movie)
        else:
            movie = create_proto_free()
            initialize_to_sheets(movie)
        write_proto(movie)

    elif sys.argv[1] == "reviews_sorted":
        print(reviews_sorted())   
    
    elif sys.argv[1] == "post_to_sheets":

        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        review = print_review(proto, filename)
        
        post_to_sheets(proto, review)
    elif sys.argv[1] == "post_to_letterboxd":
        
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        short_review = print_short_review(proto, filename)

        post_to_letterboxd(proto, short_review)
    elif sys.argv[1] == "post_to_imdb":

        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        imdb_review = print_imdb_review(proto, filename)

        post_to_imdb(proto, imdb_review)
        
    elif sys.argv[1] == "post_to_all":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        review = print_review(proto, filename)
        short_review = print_short_review(proto, filename)
        imdb_review = print_imdb_review(proto, filename)

        # Post to Sheets and Letterboxd
        p_sheets = mp.Process(target=post_to_sheets, args=(proto, review))
        p_letterboxd = mp.Process(target=post_to_letterboxd, args=(copy.deepcopy(proto), short_review))
        p_imdb = mp.Process(target=post_to_imdb, args=(copy.deepcopy(proto), imdb_review))

        p_sheets.start()
        p_letterboxd.start()
        p_sheets.join()
        p_letterboxd.join()
        p_imdb.start()
        p_imdb.join()
    else:
        print("Invalid input. Please try again.")