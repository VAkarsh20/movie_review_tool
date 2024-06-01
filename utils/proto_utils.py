import os
from google.protobuf import text_format
from protos import movie_pb2
from . wikipedia_utils import get_wiki_info
from . date_utils import get_review_date
from . text_utils import get_filename
import pandas as pd

# Read and Write functions
def read_proto(filename):
    with open("movies_textproto/" + filename + ".textproto", "r") as fd:
        text_proto = fd.read()
        
        fd.seek(0)
        if len(fd.readlines()) <= 8:
            return text_format.Parse(text_proto, movie_pb2.MovieFree())
        else: 
            # TODO: Try Catch for old Proto Format
            return text_format.Parse(text_proto, movie_pb2.Movie())

def write_proto(proto):

    filename = get_filename(proto.title, proto.release_year)
    path = ("movies_textproto/" + filename)
    if not os.path.exists(filename):
        with open(path, "w") as fd:
            text_proto = text_format.MessageToString(proto)
            fd.write(text_proto)
    else:
        print("File already exists! Either choose different file or move current to redux.")

# Create functions
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
    return movie_pb2.Movie(title=title, rating=0.1, review=review, release_year = find_release_year(infobox), review_date = get_review_date(), redux=redux, id=set_id(imdb_id, redux), imdb_id=imdb_id)

def create_proto_free(redux=False):
    title, imdb_id, infobox = get_wiki_info()
    return movie_pb2.MovieFree(title=title, rating=0.1, review="", release_year = find_release_year(infobox), review_date = get_review_date(), redux=redux, id=set_id(imdb_id, redux), imdb_id=imdb_id)

# Helper functions
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
        direction.comments = "macroscale is; microscale is; direction of actors is; storytelling is; tension is"
        return direction
    elif key == "Music by":
        score = movie_pb2.Movie.Review.Score()
        score.composer.extend(person_list)
        score.rating = "TODO"
        score.comments = "TODO"
        return score
    elif key == "Cinematography":
        cinematography = movie_pb2.Movie.Review.Cinematography()
        cinematography.cinematographer.extend(person_list)
        cinematography.rating = "TODO"
        cinematography.comments = "TODO"
        return cinematography
    elif key == "Edited by":
        editing = movie_pb2.Movie.Review.Editing()
        editing.editor.extend(person_list)
        editing.rating = "TODO"
        editing.comments = "TODO"
        return editing

    return None  

def get_generic(category):
    # Create generic object
    return movie_pb2.Movie.Review.GenericCategory(rating="TODO", comments = "TODO")

# TODO: Make Try Catch for if there is no Acting field
def get_acting(infobox):
    # Create acting object
    acting = movie_pb2.Movie.Review.Acting()

    # Parse all of the possible actors (with their comments) and append them to the object
    for name in infobox["Starring"]:
        performance = movie_pb2.Movie.Review.Acting.Performance(actor = movie_pb2.Movie.Review.Person(name = name))
        performance.rating = "TODO"
        performance.comments = "TODO"
        acting.performance.append(performance)

    # Add comments on the overall cast
    acting.cast.CopyFrom(get_generic("TODO"))

    # Overall Rating on Acting
    acting.rating = ""

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
        story.comments = "The concept is; the plot structure is; flow between sequences is; character writing is"
        screenplay.rating = "TODO"
        screenplay.comments = "The dialogue is; the humor is; the symbolism is; the foreshadowing is"

    return story, screenplay


def find_release_year(infobox):
    # Find the release year for the movie
    release_key = "Release dates" if "Release dates" in infobox else "Release date"
    release_year = infobox[release_key][0]
    return int(release_year.split('\xa0')[2]) if '\xa0' in release_year else int(release_year.partition(", ")[-1].partition(" ")[0])


# TODO: Do this without PD
def set_id(imdb_id=None, redux=False):
    if redux:
        df = pd.read_csv("movies.csv")
        return int(df[df["imdbID"] == imdb_id]["Id"])
    else:
        return len(os.listdir('movies_textproto/'))
    
# Sanity checks
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