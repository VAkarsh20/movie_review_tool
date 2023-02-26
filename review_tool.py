import movie_pb2
import string
import requests
from bs4 import BeautifulSoup
import requests
import sys
from google.protobuf import text_format
from sheets import post_to_sheets, reviews_sorted
from datetime import datetime
from letterboxd import LetterboxdBot
import os
import wikipedia

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
    return None, None, None

def get_imdb_id(film):

    links = wikipedia.WikipediaPage(title=film).references
    imdb_id = [x.replace("https://www.imdb.com/title/","").partition("/")[0] for x in links if("https://www.imdb.com/title/" in x)]

    if len(imdb_id) > 1 and len(set(imdb_id)) > 1:
        raise Exception("More than one IMDB link for " + film)

    imdb_id = imdb_id[0]
    return imdb_id

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

def parse_direction(infobox):
    
    # Create direction object
    direction = movie_pb2.Movie.Review.Direction()

    # Parse all of the possible directors and append them to the object
    for name in infobox["Directed by"]:
        director = movie_pb2.Movie.Review.Person()
        director.name = name
        direction.director.append(director)

    # Add comments for the direction
    direction.comments = "Direction ()"

    return direction


def parse_acting(infobox):
    
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


def parse_writing(infobox):
    
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


def parse_score(infobox):
    
    # See if movie has a score
    if "Music by" not in infobox:
        return None

    # Create score object
    score = movie_pb2.Movie.Review.Score()

    # Parse all of the possible composers and append them to the object
    for name in infobox["Music by"]:
        composer = movie_pb2.Movie.Review.Person()
        composer.name = name
        score.composer.append(composer)

    # Add comments for the score
    score.comments = "Score ()"

    return score

def parse_cinematography(infobox):

    # See if movie has cinematography
    if "Cinematography" not in infobox:
        return None
    
    # Create cinematography object
    cinematography = movie_pb2.Movie.Review.Cinematography()

    # Parse all of the possible cinematographers and append them to the object
    for name in infobox["Cinematography"]:
        cinematographer = movie_pb2.Movie.Review.Person()
        cinematographer.name = name
        cinematography.cinematographer.append(cinematographer)

    # Add comments for the cinematography
    cinematography.comments = "Cinematography ()"

    return cinematography


def parse_editing(infobox):
    
    # Create score object
    editing = movie_pb2.Movie.Review.Editing()

    # Parse all of the possible composers and append them to the object
    for name in infobox["Edited by"]:
        editor = movie_pb2.Movie.Review.Person()
        editor.name = name
        editing.editor.append(editor)

    # Add comments for the score
    editing.comments = "Editing ()"

    return editing

def find_release_year(infobox):
    
    # Find the release year for the movie
    release_key = "Release dates" if "Release dates" in infobox else "Release date"
    release_year = infobox[release_key][0]
    return int(release_year.split('\xa0')[2]) if '\xa0' in release_year else int(release_year.partition(", ")[-1].partition(" ")[0])

def find_review_date():
    
    # Set the review date
    today = datetime.now()
    return "{}/{}/{}".format(today.strftime('%m'), today.strftime('%d'), today.strftime('%Y')) 

def create_proto():
    
    # Find title
    title, imdb_id, infobox = get_wiki_info()

    # Initializing all the fields
    direction = parse_direction(infobox)
    acting = parse_acting(infobox)
    story, screenplay = parse_writing(infobox)
    score = parse_score(infobox)
    cinematography = parse_cinematography(infobox)
    sound = "Sound ()"
    editing = parse_editing(infobox)
    visual_effects = "Visual Effects ()"
    production_design = "Production Design ()"
    makeup = "Makeup ()"
    costumes = "Costumes ()"
    plot_structure = "Plot Structure "
    pacing = "Pacing "
    climax = "Climax "
    tone = "Tone"
    final_notes = ""
    overall = "Overall, "

    # Creating the review object
    review = movie_pb2.Movie.Review(
        direction=direction, 
        acting=acting,
        story=story,
        screenplay=screenplay,
        score=score,
        cinematography=cinematography,
        sound=sound,
        editing=editing,
        visual_effects=visual_effects,
        production_design=production_design,
        makeup=makeup,
        costumes=costumes,
        plot_structure=plot_structure,
        pacing=pacing,
        climax=climax,
        tone=tone,
        final_notes=final_notes,
        overall=overall
    )

    # Get release year
    release_year = find_release_year(infobox)

    # Get review date
    review_date = find_review_date()

    # creating the review object from the fields already initialized
    return movie_pb2.Movie(title=title, rating=1.0, review=review, release_year=release_year, review_date=review_date, redux=False, id=-1, imdb_id=imdb_id)
    

def create_proto_free():
    title, imdb_id, infobox = get_wiki_info()
    release_year = find_release_year(infobox)
    review_date = find_review_date()
    return movie_pb2.MovieFree(title=title, rating=1.0, review="", release_year=release_year, review_date=review_date, redux=False, id=-1, imdb_id=imdb_id)


def write_proto(proto):

    filename = ("movies_textproto/" + proto.title + " ({})".format(proto.release_year) + ".textproto").replace(":","")
    if not os.path.exists(filename):
        with open(filename, "w") as fd:
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


def print_review(proto, filename):

    if proto.redux == True and filename != "":
        return print_redux_review(proto, filename)

    if isinstance(proto, movie_pb2.MovieFree):
        return proto.review

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
    review += ". "

    review += proto.review.overall + "."

    return review

if __name__=="__main__":
    
    argc = len(sys.argv)

    if argc == 1 or sys.argv[1] == "create_proto":
        movie = create_proto()
        write_proto(movie)

    elif sys.argv[1] == "create_proto_free":
        movie = create_proto_free()
        write_proto(movie)

    elif sys.argv[1] == "reviews_sorted":
        print(reviews_sorted())   
    
    elif sys.argv[1] == "post_review":

        filename = input("What is the name of the movie?\n")
        proto = read_proto(filename)
        review = print_review(proto, filename)
        # post_to_sheets(proto.title, proto.rating, review, proto.review_date)
    elif sys.argv[1] == "post_to_letterboxd":
        
        filename = input("What is the name of the movie?\n")
        username = input("What is your username?\n")
        password = input("What is your password?\n")
        
        proto = read_proto(filename)
        letterboxd_bot = LetterboxdBot()
        letterboxd_bot.login(username, password)
        letterboxd_bot.log_film(proto)

    else:
        print("Invalid input. Please try again.")