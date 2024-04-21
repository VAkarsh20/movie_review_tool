from . proto_utils import *
import movie_pb2

def print_review(proto, filename):
    if proto.redux == True and filename != "":
        return print_redux_review(proto, filename)

    if isinstance(proto, movie_pb2.MovieFree):
        return proto.review

    review = combine_review_fields(proto, filename)
    review += ". "

    review += proto.review.overall + "."

    return review

def print_redux_review(redux_proto, filename):
    
    #Format is REDUX (YEAR): <Review>. ORIGINAL (RATING, YEAR): <Review>. 
    redux = "REDUX {}: ".format(redux_proto.review_date) + print_review(redux_proto, "")
    original_proto = read_proto("reduxed/" + filename)
    original = " ORIGINAL ({}, {}): ".format(original_proto.rating, original_proto.review_date) + print_review(original_proto, "")    
    return redux + original

def print_short_review(proto, filename):
    if proto.redux == True and filename != "":
        return print_short_redux_review(proto, filename)
    
    if isinstance(proto, movie_pb2.MovieFree):
        return "Rating: {}\n{}".format(proto.rating, proto.review)
    else:
        return "Rating: {}\n{}.".format(proto.rating, proto.review.overall)

def print_short_redux_review(redux_proto, filename):
    
    #Format is REDUX (YEAR): <Review>. ORIGINAL (RATING, YEAR): <Review>. 
    redux = "REDUX ({})\n{}\n\n".format(redux_proto.review_date, print_short_review(redux_proto, ""))
    original_proto = read_proto("reduxed/" + filename)
    original = "ORIGINAL ({})\n{}".format(original_proto.review_date, print_short_review(original_proto, ""))  
    return redux + original
    
# Create the review to be put in a format for IMDb
def print_imdb_review(proto, filename):
    if isinstance(proto, movie_pb2.MovieFree):
        return ""
    
    is_redux = proto.redux
    
    review_parts = []
    if is_redux:
        review_parts.append("REDUX ({})".format(proto.review_date))

    review_parts.append("Rating: {}".format(proto.rating))
    
    if isinstance(proto, movie_pb2.Movie):
        full_review = combine_review_field_pretty_print(proto, filename)
        review_parts.append(full_review)
    else:
        review_parts.append(proto.review)
    
    if is_redux:
        review_parts.append("\n\nORIGINAL: ({})".format(proto.review_date))

        original_proto = read_proto("reduxed/" + filename)

        review_parts.append(print_short_review(original_proto, filename))


    review = "\n".join(review_parts)

    return review.rstrip()

def combine_review_field_pretty_print(proto, filename):
    review = []

    # Overall
    if proto.review.overall != "":
        review.append(proto.review.overall + ".")

    # Direction
    if proto.review.direction.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.direction, "Direction"))
    
    # Story
    if proto.review.story.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.story, "Story"))
    
    # Screenplay
    if proto.review.screenplay.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.screenplay, "Screenplay"))

    # Acting
    if proto.review.acting.rating != "":
        acting = []
        acting.append("Acting: " + proto.review.acting.rating)
        for actor in proto.review.acting.performance:
            acting.append(combine_rating_and_comments_new(actor, actor.actor.name, True))
        if proto.review.acting.cast.rating != "":
            acting.append(combine_rating_and_comments_new(proto.review.acting.cast, "Rest of the cast", True))
        review.append("\n".join(acting))
    
    # Score
    if proto.review.score.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.score, "Score"))
    
    # Soundtrack
    if proto.review.soundtrack.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.soundtrack, "Soundtrack"))

    # Cinematography
    if proto.review.cinematography.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.cinematography, "Cinematography"))
    
    # Editing
    if proto.review.editing.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.editing, "Editing"))
    
    # Sound
    if proto.review.sound.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.sound, "Sound"))
    
    # Visual Effects
    if proto.review.visual_effects.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.visual_effects, "Visual Effects"))
    
    # Animation
    if proto.review.animation.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.animation, "Animation"))
    
    # Production Design
    if proto.review.production_design.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.production_design, "Production Design"))

    # Makeup
    if proto.review.makeup.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.makeup, "Makeup"))

    # Costumes
    if proto.review.costumes.rating != "":
        review.append(combine_rating_and_comments_new(proto.review.costumes, "Costumes"))

    # Plot Structure
    if proto.review.plot_structure != "":
        review.append("Plot Structure\n" + proto.review.plot_structure)
    
    # Pacing
    if proto.review.pacing != "":
        review.append("Pacing\n" + proto.review.pacing)

    # Climax
    if proto.review.climax != "":
        review.append("Climax\n" + proto.review.climax)

    # Tone
    if proto.review.tone != "":
        review.append("Tone\n" + proto.review.tone)
    
    # Final Notes
    if proto.review.final_notes != "":
        review.append("Final Notes\n" + proto.review.final_notes)

    review = "\n\n".join(review)
    return review

def combine_rating_and_comments_new(field, field_name="", is_acting=False):
    rating, comments = field.rating, field.comments
    if comments == "":
        return "{}: {}".format(field_name, rating)

    if is_acting:
        return "{}: {} ({})".format(field_name, rating, comments)

    return "{}: {}\n{}".format(field_name, rating, comments)


def combine_rating_and_comments(field, fieldname=""):

    rating, comments = field.rating, field.comments
    if comments == "":
        return "{} {}".format(rating, fieldname)

    return "{} {} ({})".format(rating, fieldname, comments)

def combine_review_fields(proto, filename):
    
    review = []
    
    # Direction
    if proto.review.direction != "":
        review.append(combine_rating_and_comments(proto.review.direction, "Direction"))
    
    # Acting
    if proto.review.acting != "":
        acting = proto.review.acting.rating + " Acting ("
        for actor in proto.review.acting.performance:
            acting += "{}, ".format(combine_rating_and_comments(actor, "from " + actor.actor.name))
        acting += combine_rating_and_comments(proto.review.acting.cast, "from the rest of the cast") + ")"
        review.append(acting)

    # Story
    if proto.review.story.comments != "":
        review.append(combine_rating_and_comments(proto.review.story, "Story"))

    # Screenplay
    if proto.review.screenplay.comments != "":
        review.append(combine_rating_and_comments(proto.review.screenplay, "Screenplay"))

    # Score
    if proto.review.score.comments != "":
        review.append(combine_rating_and_comments(proto.review.score, "Score"))
    
    # Cinematography
    if proto.review.cinematography.comments != "":
        review.append(combine_rating_and_comments(proto.review.cinematography, "Cinematography"))

    # Editing
    if proto.review.editing.comments != "":
        review.append(combine_rating_and_comments(proto.review.editing, "Editing"))

    # Sound
    if proto.review.sound.comments != "":
        review.append(combine_rating_and_comments(proto.review.sound, "Sound"))
    
    # Visual Effects
    if proto.review.visual_effects.comments != "":
        review.append(combine_rating_and_comments(proto.review.visual_effects, "Visual Effects"))

    # Animation
    if proto.review.visual_effects.comments != "":
        review.append(combine_rating_and_comments(proto.review.visual_effects, "Animation"))
    
    # Production Design
    if proto.review.production_design.rating != "":
        review.append(combine_rating_and_comments(proto.review.production_design, "Production Design"))

    # Makeup
    if proto.review.makeup.rating != "":
        review.append(combine_rating_and_comments(proto.review.makeup, "Makeup"))
        review.append(proto.review.makeup.comments)

    # Costumes
    if proto.review.costumes.rating != "":
        review.append(combine_rating_and_comments(proto.review.costumes, "Costumes"))

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