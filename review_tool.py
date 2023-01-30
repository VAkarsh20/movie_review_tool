import movie_pb2
import string
import requests
from bs4 import BeautifulSoup
import requests
import sys
from google.protobuf import text_format
from sheets import post_to_sheets, reviews_sorted
from datetime import date
from letterboxd import LetterboxdBot


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

def parse_direction():
    
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


def parse_acting():
    
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
    acting.comments = " Acting "

    return acting


def parse_writing():
    
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
    else:
        for name in infobox["Story by"]:
            writer = movie_pb2.Movie.Review.Person()
            writer.name = name
            story.writer.append(writer)

        for name in infobox["Screenplay by"]:
            writer = movie_pb2.Movie.Review.Person()
            writer.name = name
            screenplay.writer.append(writer)

    # Add comments for the writing
    story.comments = "Story ()"
    screenplay.comments = "Screenplay ()"

    return story, screenplay


def parse_score():
    
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

def parse_cinematography():
    
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


def parse_editing():
    
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

def create_proto():

    title = ""
    # Parse Wikipedia
    global infobox 
    parsed_wikipedia = False
    
    while not parsed_wikipedia:
        try: 
            title = input("What is the film title?\n")
            wiki_title = title.replace(" ", "_")
            infobox = parse_wiki("https://en.wikipedia.org/wiki/" + wiki_title)
            
            # Change the film title if it has a (film) tag end the end of the wikipedia search
            if title.endswith("film)"):
                title = title[:title.rfind(' (')]
            
            parsed_wikipedia = True
        except:
            print("Film not found. Please try again.")

    # Initializing all the fields
    direction = parse_direction()
    acting = parse_acting()
    story, screenplay = parse_writing()
    score = parse_score()
    cinematography = parse_cinematography()
    sound = "Sound ()"
    editing = parse_editing()
    visual_effects = "Visual Effects ()"
    production_design = "Production Design ()"
    makeup = "Makeup ()"
    costumes = "Costumes ()"
    plot_structure = "Plot Structure "
    pacing = "Pacing "
    climax = "climax "
    tone = "tone"
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

    # Find the release year for the movie
    release_year = int(infobox["Release dates"][0].split('\xa0')[2])

    # Set the review date
    today = date.today()
    review_date = "{}/{}/{}".format(today.month, today.day, today.year) 

    # creating the review object from the fields already initialized
    movie = movie_pb2.Movie(title=title, rating=0.0, review=review, release_year=release_year, review_date=review_date)
    return movie

def write_proto(proto):
    with open("movies_textproto/" + proto.title + " ({})".format(proto.release_year) + ".textproto", "w") as fd:
        text_proto = text_format.MessageToString(proto)
        fd.write(text_proto)

def read_proto(filename):
    with open("movies_textproto/" + filename + ".textproto", "r") as fd:
        text_proto = fd.read()

    return text_format.Parse(text_proto, movie_pb2.Movie())

def proto_to_string(proto):

    review = ""
    
    # Direction
    review += proto.review.direction.comments + ", "
    
    # Acting
    acting = proto.review.acting.comments + " ("
    for actor in proto.review.acting.actor:
        acting += actor.comments + ", "
    acting += proto.review.acting.cast + ")"
    review += acting + ", "

    # Story
    review += proto.review.story.comments + ", "

    # Screenplay
    review += proto.review.screenplay.comments + ", "

    # Score
    review += proto.review.score.comments + ", "
    
    # Cinematography
    review += proto.review.cinematography.comments + ", "

    # Sound
    if proto.review.sound != "":
        review += proto.review.sound + ", "

    # Editing
    review += proto.review.editing.comments + ", "
    
    # Visual Effects
    if proto.review.visual_effects != "":
        review += proto.review.visual_effects + ", "
    
    # Production Design
    if proto.review.production_design != "":
        review += proto.review.production_design + ", "

    # Makeup
    if proto.review.makeup != "":
        review += proto.review.makeup + ", "

    # Costumes
    if proto.review.costumes != "":
        review += proto.review.costumes + ", "

    # Plot Structure
    review += proto.review.plot_structure + ", "
    
    # Pacing
    review += proto.review.plot_structure + ", "

    # Climax
    review += proto.review.climax + ", "

    # Tone
    review += proto.review.tone + ", "
    
    # Final Notes
    if proto.review.final_notes != "":
        review += proto.review.final_notes

    review = review.rstrip(", ")
    review += ". "

    review += proto.review.overall + "."

    post_to_sheets(proto.title, proto.rating, review)

if __name__=="__main__":
    
    argc = len(sys.argv)

    if argc == 1 or sys.argv[1] == "create_proto":
        movie = create_proto()
        write_proto(movie)

    elif sys.argv[1] == "reviews_sorted":
        print(reviews_sorted())   
    
    elif sys.argv[1] == "proto_to_string":

        filename = input("What is the name of the movie?\n")
        proto = read_proto(filename)
        proto_to_string(proto)
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