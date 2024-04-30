from . proto_utils import *
from protos import movie_pb2

def print_review(proto, filename, is_pretty=False):
    if proto.redux == True and filename != "":
        return print_redux_review(proto, filename)

    if isinstance(proto, movie_pb2.MovieFree):
        return proto.review

    return _combine_review_field(proto, is_pretty)

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
    
    review_parts = []
    if proto.redux:
        review_parts.append("REDUX ({})".format(proto.review_date))

    review_parts.append("Rating: {}".format(proto.rating))
    
    if isinstance(proto, movie_pb2.Movie):
        full_review = _combine_review_field(proto, True)
        review_parts.append(full_review)
    else:
        review_parts.append(proto.review)
    
    if proto.redux:
        review_parts.append("\n\nORIGINAL: ({})".format(proto.review_date))
        original_proto = read_proto("reduxed/" + filename)
        review_parts.append(print_short_review(original_proto, filename))

    return "\n".join(review_parts).rstrip()

def _combine_review_field(proto, is_pretty):
    review = []

    # Direction
    if proto.review.direction.rating != "":
        review.append(_combine_rating_and_comments(proto.review.direction, "Direction", is_pretty))

    # Story
    if proto.review.story.rating != "":
        review.append(_combine_rating_and_comments(proto.review.story, "Story", is_pretty))
    
    # Screenplay
    if proto.review.screenplay.rating != "":
        review.append(_combine_rating_and_comments(proto.review.screenplay, "Screenplay", is_pretty))

    # Acting
    if proto.review.acting.rating != "":
        acting = []
        if is_pretty:
            acting.append("Acting: " + proto.review.acting.rating)
            for actor in proto.review.acting.performance:
                acting.append(_combine_rating_and_comments(actor, actor.actor.name, is_pretty, True))
            if proto.review.acting.cast.rating != "":
                acting.append(_combine_rating_and_comments(proto.review.acting.cast, "Rest of the cast", is_pretty, True))
            review.append("\n".join(acting))
        else:
            acting.append(proto.review.acting.rating + " Acting (")
            for actor in proto.review.acting.performance:
                acting.append("{}, ".format(_combine_rating_and_comments(actor, "from " + actor.actor.name)))
            if proto.review.acting.cast.rating != "":
                acting.append(_combine_rating_and_comments(proto.review.acting.cast, "from the rest of the cast") + ")")
            else:
                # Close the Acting field
                acting[-1] = acting[-1][:-2] + ")"
            review.append("".join(acting))

    # Score
    if proto.review.score.rating != "":
        review.append(_combine_rating_and_comments(proto.review.score, "Score", is_pretty))
    
    # Soundtrack
    if proto.review.soundtrack.rating != "":
        review.append(_combine_rating_and_comments(proto.review.soundtrack, "Soundtrack", is_pretty))

    # Cinematography
    if proto.review.cinematography.rating != "":
        review.append(_combine_rating_and_comments(proto.review.cinematography, "Cinematography", is_pretty))
    
    # Editing
    if proto.review.editing.rating != "":
        review.append(_combine_rating_and_comments(proto.review.editing, "Editing", is_pretty))
    
    # Sound
    if proto.review.sound.rating != "":
        review.append(_combine_rating_and_comments(proto.review.sound, "Sound", is_pretty))
    
    # Visual Effects
    if proto.review.visual_effects.rating != "":
        review.append(_combine_rating_and_comments(proto.review.visual_effects, "Visual Effects", is_pretty))
    
    # Animation
    if proto.review.animation.rating != "":
        review.append(_combine_rating_and_comments(proto.review.animation, "Animation", is_pretty))
    
    # Production Design
    if proto.review.production_design.rating != "":
        review.append(_combine_rating_and_comments(proto.review.production_design, "Production Design", is_pretty))

    # Makeup
    if proto.review.makeup.rating != "":
        review.append(_combine_rating_and_comments(proto.review.makeup, "Makeup", is_pretty))

    # Costumes
    if proto.review.costumes.rating != "":
        review.append(_combine_rating_and_comments(proto.review.costumes, "Costumes", is_pretty)) 
    
    # Plot Structure
    if proto.review.plot_structure != "":
        plot_structure = proto.review.plot_structure
        if is_pretty:
            plot_structure = "Plot Structure\n" + proto.review.plot_structure
        review.append(plot_structure)
    
    # Pacing
    if proto.review.pacing != "":
        pacing = proto.review.pacing
        if is_pretty:
            pacing = "Pacing\n" + proto.review.pacing
        review.append(pacing)

    # Climax
    if proto.review.climax != "":
        climax = proto.review.climax
        if is_pretty:
            climax = "Climax\n" + proto.review.climax
        review.append(climax)

    # Tone
    if proto.review.tone != "":
        tone = proto.review.tone
        if is_pretty:
            tone = "Tone\n" + proto.review.tone
        review.append(tone)
    
    # Final Notes
    if proto.review.final_notes != "":
        final_notes = proto.review.final_notes
        if is_pretty:
            final_notes = "Final Notes\n" + proto.review.final_notes
        review.append(final_notes)
    
    if is_pretty:
        review.insert(0, proto.review.overall + ".")
        return "\n\n".join(review)
    else:
        return ", ".join(review) + ". {}.".format(proto.review.overall)

def _combine_rating_and_comments(field, field_name="", is_pretty=False, is_acting=False):
    rating, comments = field.rating, field.comments

    if comments == "":
        if is_pretty:
            return "{}: {}".format(field_name, rating)
        else:
            return "{} {}".format(rating, field_name)
    
    if is_pretty:
        if is_acting:
            return "{}: {} ({})".format(field_name, rating, comments)
        
        return "{}: {}\n{}".format(field_name, rating, comments)
    else:
        return "{} {} ({})".format(rating, field_name, comments)
