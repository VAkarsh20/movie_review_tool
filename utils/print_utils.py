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
    review = print_short_review(proto, filename)
    
    if isinstance(proto, movie_pb2.Movie):

        full_review = combine_review_fields(proto, filename)

        review_parts = review.split("\n\n")
        review_parts.insert(1, "\n\n{}\n\n".format(full_review))

        review = "".join(review_parts)

    return review.rstrip()

def combine_rating_and_comments(field):
    return "{} {}".format(field.rating, field.comments)

def combine_review_fields(proto, filename):
    
    review = []
    
    # Direction
    if proto.review.direction != "":
        review.append(combine_rating_and_comments(proto.review.direction))
    
    # Acting
    if proto.review.acting != "":
        acting = proto.review.acting.comments + " Acting ("
        for actor in proto.review.acting.performance:
            acting += "{}, ".format(combine_rating_and_comments(actor))
        acting += combine_rating_and_comments(proto.review.acting.cast) + ")"
        review.append(acting)

    # Story
    if proto.review.story.comments != "":
        review.append(combine_rating_and_comments(proto.review.story))

    # Screenplay
    if proto.review.screenplay.comments != "":
        review.append(combine_rating_and_comments(proto.review.screenplay))

    # Score
    if proto.review.score.comments != "":
        review.append(combine_rating_and_comments(proto.review.score))
    
    # Cinematography
    if proto.review.cinematography.comments != "":
        review.append(combine_rating_and_comments(proto.review.cinematography))

    # Editing
    if proto.review.editing.comments != "":
        review.append(combine_rating_and_comments(proto.review.editing))

    # Sound
    if proto.review.sound.comments != "":
        review.append(combine_rating_and_comments(proto.review.sound))
    
    # Visual Effects
    if proto.review.visual_effects.comments != "":
        review.append(combine_rating_and_comments(proto.review.visual_effects))
    
    # Production Design
    if proto.review.production_design.rating != "":
        review.append(combine_rating_and_comments(proto.review.production_design))

    # Makeup
    if proto.review.makeup.rating != "":
        review.append(combine_rating_and_comments(proto.review.makeup))
        review.append(proto.review.makeup.comments)

    # Costumes
    if proto.review.costumes.rating != "":
        review.append(combine_rating_and_comments(proto.review.costumes))
        review.append(proto.review.costumes.comments)

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