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

def get_wiki_info():
    
    # Parse Wikipedia
    while True:
        try:
            title = input("What is the film title?\n")
            wiki_title = title.replace(" ", "_")
            
            imdb_id = get_imdb_id(wiki_title)
            infobox = parse_wiki("https://en.wikipedia.org/wiki/" + wiki_title)
            
            # Change the film title if it has a (film) tag end the end of the wikipedia search
            if title.endswith("film)"):
                title = title[:title.rfind(' (')]
            
            return title, imdb_id, infobox
        except:
            print("Film not found. Please try again.")
            break
    return None, None, None

def get_imdb_id(film):
    
    links = " ".join(wikipedia.WikipediaPage(title=film).references)
    imdb_id = set(re.findall(pattern = "tt[0-9]+", string=links))
    # imdb_id = [x.replace("https://www.imdb.com/title/","").partition("/")[0] for x in links if("https://www.imdb.com/title/" in x)]

    # if len(imdb_id) > 1 and len(set(imdb_id)) > 1:
    if len(imdb_id) > 1:
        raise Exception("More than one IMDB link for " + film)

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
        direction.comments = "Direction ()"
        return direction
    elif key == "Music by":
        score = movie_pb2.Movie.Review.Score()
        score.composer.extend(person_list)
        score.comments = "Score ()"
        return score
    elif key == "Cinematography":
        cinematography = movie_pb2.Movie.Review.Cinematography()
        cinematography.cinematographer.extend(person_list)
        cinematography.comments = "Cinematography ()"
        return cinematography
    elif key == "Edited by":
        editing = movie_pb2.Movie.Review.Editing()
        editing.editor.extend(person_list)
        editing.comments = "Editing ()"
        return editing

    return None  


def get_acting(infobox):
    
    # Create acting object
    acting = movie_pb2.Movie.Review.Acting()

    # Parse all of the possible actors (with their comments) and append them to the object
    for name in infobox["Starring"]:
        actor = movie_pb2.Movie.Review.Person()
        actor.name = name
        actor.comments = " from " + name + " ()"
        acting.actor.append(actor)

    # Add comments on the overall cast
    acting.cast = "from the rest of the cast ()"

    # Overall Comments on Acting
    acting.comments = " Acting"

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
        story.comments = "Story ()"
        screenplay.comments = "Screenplay ()"

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
        sound = "Sound ()",
        editing = get_field(infobox, "Edited by"), # parse_editing(infobox),
        visual_effects = "Visual Effects ()",
        production_design = "Production Design ()",
        makeup = "Makeup ()",
        costumes = "Costumes ()",
        plot_structure= "Plot Structure ",
        pacing = "Pacing ",
        climax = "Climax ",
        tone = "Tone ",
        final_notes = "",
        overall = "Overall, "
    )

    # creating the review object from the fields already initialized
    return movie_pb2.Movie(title=title, rating=1.0, review=review, release_year = find_release_year(infobox), review_date = find_review_date(), redux=redux, id=len(os.listdir('movies_textproto/')), imdb_id=imdb_id)
    

def create_proto_free(redux=False):
    title, imdb_id, infobox = get_wiki_info()
    return movie_pb2.MovieFree(title=title, rating=1.0, review="", release_year = find_release_year(infobox), review_date = find_review_date(), redux=redux, id=len(os.listdir('movies_textproto/')), imdb_id=imdb_id)


def write_proto(proto):

    filename = (proto.title + " ({})".format(proto.release_year) + ".textproto").replace(":","").replace("/", " ")
    path = ("movies_textproto/" + filename)
    if not os.path.exists(filename):
        with open(path, "w") as fd:
            text_proto = text_format.MessageToString(proto)
            fd.write(text_proto)
    else:
        print("File already exists! Either choose different file or move current to redux.")

def read_proto(filename):
    with open("movies_textproto/" + filename + ".textproto", "r") as fd:
        text_proto = fd.read()
        
        fd.seek(0)
        if len(fd.readlines()) <= 8:
            return text_format.Parse(text_proto, movie_pb2.MovieFree())
        else: 
            return text_format.Parse(text_proto, movie_pb2.Movie())

def print_redux_review(redux_proto, filename):
    
    #Format is REDUX (YEAR): <Review>. ORIGINAL (RATING, YEAR): <Review>. 
    redux = "REDUX {}: ".format(redux_proto.review_date) + print_review(redux_proto, "")
    original_proto = read_proto("reduxed/" + filename)
    original = " ORIGINAL ({}, {}): ".format(original_proto.rating, original_proto.review_date) + print_review(original_proto, "")    
    return redux + original

def print_short_redux_review(redux_proto, filename):
    
    #Format is REDUX (YEAR): <Review>. ORIGINAL (RATING, YEAR): <Review>. 
    redux = "REDUX ({})\n{}\n\n".format(redux_proto.review_date, print_short_review(redux_proto, ""))
    original_proto = read_proto("reduxed/" + filename)
    original = "ORIGINAL ({})\n{}".format(original_proto.review_date, print_short_review(original_proto, ""))  
    return redux + original

def print_short_review(proto, filename):
    
    if proto.redux == True and filename != "":
        return print_short_redux_review(proto, filename)
    
    if isinstance(proto, movie_pb2.MovieFree):
        return "Rating: {}\n{}".format(proto.rating, proto.review)
    else:
        return "Rating: {}\n{}.".format(proto.rating, proto.review.overall)

def combine_review_fields(proto, filename):
    
    review = []
    
    # Direction
    if proto.review.direction != "":
        review.append(proto.review.direction.comments)
    
    # Acting
    if proto.review.acting != "":
        acting = proto.review.acting.comments + " ("
        for actor in proto.review.acting.actor:
            acting += actor.comments + ", "
        acting += proto.review.acting.cast + ")"
        review.append(acting)

    # Story
    if proto.review.story.comments != "":
        review.append(proto.review.story.comments)

    # Screenplay
    if proto.review.screenplay.comments != "":
        review.append(proto.review.screenplay.comments)

    # Score
    if proto.review.score.comments != "":
        review.append(proto.review.score.comments)
    
    # Cinematography
    if proto.review.cinematography.comments != "":
        review.append(proto.review.cinematography.comments)

    # Sound
    if proto.review.sound != "":
        review.append(proto.review.sound)

    # Editing
    if proto.review.editing.comments != "":
        review.append(proto.review.editing.comments)
    
    # Visual Effects
    if proto.review.visual_effects != "":
        review.append(proto.review.visual_effects)
    
    # Production Design
    if proto.review.production_design != "":
        review.append(proto.review.production_design)

    # Makeup
    if proto.review.makeup != "":
        review.append(proto.review.makeup)

    # Costumes
    if proto.review.costumes != "":
        review.append(proto.review.costumes)

    # Plot Structure
    if proto.review.plot_structure != "":
        review.append(proto.review.plot_structure)
    
    # Pacing
    if proto.review.pacing != "":
        review.append(proto.review.pacing)

    # Climax
    if proto.review.climax != "":
        review.append(proto.review.climax)

    # Tone
    if proto.review.tone != "":
        review.append(proto.review.tone)
    
    # Final Notes
    if proto.review.final_notes != "":
        review.append(proto.review.final_notes)

    review = ", ".join(review)
    return review

def print_review(proto, filename):

    if proto.redux == True and filename != "":
        return print_redux_review(proto, filename)

    if isinstance(proto, movie_pb2.MovieFree):
        return proto.review

    review = combine_review_fields(proto, filename)
    review += ". "

    review += proto.review.overall + "."

    return review

# Create the review to be put in a format for IMDb
def print_imdb_review(proto, filename):
    review = print_short_review(proto, filename)
    
    if isinstance(proto, movie_pb2.Movie):

        full_review = combine_review_fields(proto, filename)

        review_parts = review.split("\n\n")
        review_parts.insert(1, "\n\n{}\n\n".format(full_review))

        review = "".join(review_parts)

    return review.rstrip()

def move_redux_reviews(filename):
    
    path = "movies_textproto/"
    count = 0
    while os.path.exists(path + ("reduxed/" * count) + filename):
        count += 1
    
    if not os.path.exists(path + ("reduxed/" * count)):
        os.mkdir(path + ("reduxed/" * count))

    while count > 0:
        os.rename(path + ("reduxed/" * (count - 1)) + filename, path + ("reduxed/" * (count)) + filename)
        count -= 1

def reviews_sorted():

    # Getting all the Titles and Ratings
    df = pd.read_csv("movies.csv")[["Title", "Rating"]]

    # Sortings in descending order and returning as a string
    df = df.sort_values(by=['Rating'], ascending=False)
    return df.to_string(index=False)

if __name__=="__main__":
    
    argc = len(sys.argv)

    # Reset clock
    subprocess.run(["sudo", "hwclock", "-s"])

    if argc == 1 or sys.argv[1] == "create_proto":
        if argc > 3 and sys.argv[2] == "redux":
            subprocess()
            movie = create_proto(True)
            move_redux_reviews("{} ({})".format(movie.title, movie.release_year))
            initialize_to_sheets(movie)
            write_proto(movie)
        else:
            movie = create_proto()
            initialize_to_sheets(movie)
            write_proto(movie)
    
    elif sys.argv[1] == "create_proto_free":
        if argc > 3 and sys.argv[2] == "redux":
            movie = create_proto(True)
            move_redux_reviews("{} ({})".format(movie.title, movie.release_year))
            initialize_to_sheets(movie)
            write_proto(movie)
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
        review = print_review(proto, filename)
        
        post_to_sheets(proto, review)
    elif sys.argv[1] == "post_to_letterboxd":
        
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        short_review = print_short_review(proto, filename)

        post_to_letterboxd(proto, short_review)
    elif sys.argv[1] == "post_to_imdb":

        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        imdb_review = print_imdb_review(proto, filename)

        post_to_imdb(proto, imdb_review)
        
    elif sys.argv[1] == "post_to_all":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        review = print_review(proto, filename)
        short_review = print_short_review(proto, filename)
        imdb_review = print_imdb_review(proto, filename)

        # Post to Sheets and Letterboxd
        p_sheets = mp.Process(target=post_to_sheets, args=(proto, review))
        p_letterboxd = mp.Process(target=post_to_letterboxd, args=(copy.deepcopy(proto), short_review))
        p_imdb = mp.Process(target=post_to_imdb, args=(copy.deepcopy(proto), imdb_review))

        p_sheets.start()
        p_letterboxd.start()
        p_imdb.start()

        p_sheets.join()
        p_letterboxd.join()
        p_imdb.join()
    else:
        print("Invalid input. Please try again.")