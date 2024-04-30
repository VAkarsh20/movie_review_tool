from protos import movie_pb2
from google.protobuf import text_format

# Converting functions                
def convert_direction(old_field, filename):
    field_name_error_check("Direction", old_field.comments, filename)
    missing_tier(old_field.comments, "Direction", filename)

    rating, comments = get_rating_and_comments(old_field.comments, "Direction", filename)
    new_direction = movie_pb2.Movie.Review.Direction(director = old_field.director, rating = rating)
    if comments != "":
        new_direction.comments = comments[0].capitalize() + comments[1:]

    return new_direction

def convert_acting(old_field, filename):
    field_name_error_check("Acting", old_field.comments, filename)
    missing_tier(old_field.comments, "Acting", filename)

    rating, _ = get_rating_and_comments(old_field.comments, "Acting", filename)
    new_acting = movie_pb2.Movie.Review.Acting(rating = rating)

    if old_field.cast != "":
        field_name_error_check("from the rest of the cast", old_field.cast, filename)
        missing_tier(old_field.cast, "from the rest of the cast", filename)
        cast_rating, cast_comments = get_rating_and_comments(old_field.cast, "from the rest of the cast", filename)
        cast = movie_pb2.Movie.Review.GenericCategory(rating = cast_rating)

        if cast_comments != "":
            cast.comments = cast_comments[0].capitalize() + cast_comments[1:]

        new_acting.cast.MergeFrom(cast)
    

    for actor in old_field.actor:
        field_name_error_check("from", actor.comments, filename)
        missing_tier(actor.comments, "from", filename)

        actor_rating, actor_comments = get_rating_and_comments(actor.comments, "from", filename)
        performance = movie_pb2.Movie.Review.Acting.Performance(
            actor = movie_pb2.Movie.Review.Person(name = actor.name),
            rating = actor_rating,
        )

        if actor_comments != "":
            performance.comments = actor_comments[0].capitalize() + actor_comments[1:]

        new_acting.performance.append(performance)

    return new_acting

def convert_story(old_field, filename):
    field_name_error_check("Story", old_field.comments, filename)
    missing_tier(old_field.comments, "Story", filename)

    rating, comments = get_rating_and_comments(old_field.comments, "Story", filename)
    new_story = movie_pb2.Movie.Review.Story(writer = old_field.writer, rating = rating)
    if comments != "":
        new_story.comments = comments[0].capitalize() + comments[1:]
    return new_story

def convert_screenplay(old_field, filename):
    field_name_error_check("Screenplay", old_field.comments, filename)
    missing_tier(old_field.comments, "Screenplay", filename)

    rating, comments = get_rating_and_comments(old_field.comments, "Screenplay", filename)
    new_field = movie_pb2.Movie.Review.Screenplay(writer = old_field.writer, rating = rating)
    if comments != "":
        new_field.comments = comments[0].capitalize() + comments[1:]
    return new_field

def convert_score(old_field, filename):
    field_name_error_check("Score", old_field.comments, filename)
    missing_tier(old_field.comments, "Score", filename)

    # if "soundtrack" in old_field.comments.lower():
    #     raise ValueError("There is a soundtrack in {}, handle later".format(filename))
    rating, comments = get_rating_and_comments(old_field.comments, "Score", filename)
    new_field = movie_pb2.Movie.Review.Score(composer = old_field.composer, rating = rating)
    if comments != "":
        new_field.comments = comments[0].capitalize() + comments[1:]
    return new_field

def convert_cinematography(old_field, filename):
    field_name_error_check("Cinematography", old_field.comments, filename)
    missing_tier(old_field.comments, "Cinematography", filename)

    rating, comments = get_rating_and_comments(old_field.comments, "Cinematography", filename)
    new_field = movie_pb2.Movie.Review.Cinematography(cinematographer = old_field.cinematographer, rating = rating)
    if comments != "":
        new_field.comments = comments[0].capitalize() + comments[1:]
    return new_field

def convert_editing(old_field, filename):
    field_name_error_check("Editing", old_field.comments, filename)
    missing_tier(old_field.comments, "Editing", filename)

    rating, comments = get_rating_and_comments(old_field.comments, "Editing", filename)
    new_field = movie_pb2.Movie.Review.Editing(editor = old_field.editor, rating = rating)
    if comments != "":
        new_field.comments = comments[0].capitalize() + comments[1:]
    return new_field

def convert_generic(old_field, field_name, filename):
    field_name_error_check(field_name, old_field, filename)
    missing_tier(old_field, field_name, filename)

    rating, comments = get_rating_and_comments_generic(old_field, field_name, filename)
    new_field = movie_pb2.Movie.Review.GenericCategory(rating = rating)
    if comments != "":
        new_field.comments = comments[0].capitalize() + comments[1:]
    return new_field

def convert_visual_effects(old_field, filename):
    # if "animation" in old_field.lower():
    #     raise ValueError("There is an animation in {}, handle later".format(filename))
    field_name = "Visual Effects"
    if "Animation" in old_field:
        field_name = "Animation"
        missing_tier(old_field, field_name, filename)
    else:
        field_name_error_check(field_name, old_field, filename)
        missing_tier(old_field, field_name, filename)

    rating, comments = get_rating_and_comments_generic(old_field, field_name, filename)
    new_field = movie_pb2.Movie.Review.GenericCategory(rating = rating)
    if comments != "":
        new_field.comments = comments.capitalize()
    return new_field
    

def convert_old_format_to_new(original, filename):

    review = movie_pb2.Movie.Review()

    try:
        if original.review.direction.comments != "":
            review.direction.MergeFrom(convert_direction(original.review.direction, filename))

        if original.review.acting.comments != "":
            review.acting.MergeFrom(convert_acting(original.review.acting, filename))
        
        if original.review.story.comments != "":
            review.story.MergeFrom(convert_story(original.review.story, filename))
        
        if original.review.screenplay.comments != "":
            review.screenplay.MergeFrom(convert_screenplay(original.review.screenplay, filename))

        if original.review.score.comments != "":
            review.score.MergeFrom(convert_score(original.review.score, filename))

        if original.review.soundtrack != "":
            review.soundtrack.MergeFrom(convert_generic(original.review.soundtrack, "Soundtrack", filename))
        
        if original.review.cinematography.comments != "":
            review.cinematography.MergeFrom(convert_cinematography(original.review.cinematography, filename))
        
        if original.review.editing.comments != "":
            review.editing.MergeFrom(convert_editing(original.review.editing, filename))
        
        if original.review.sound != "":
            review.sound.MergeFrom(convert_generic(original.review.sound, "Sound", filename))
        
        if original.review.visual_effects != "":
            if "Animation" in original.review.visual_effects:
                review.animation.MergeFrom(convert_generic(original.review.visual_effects, "Animation", filename))
            else:
                review.visual_effects.MergeFrom(convert_generic(original.review.visual_effects, "Visual Effects", filename))
        
        if original.review.production_design != "":
            review.production_design.MergeFrom(convert_generic(original.review.production_design, "Production Design", filename))
        
        if original.review.makeup != "":
            review.makeup.MergeFrom(convert_generic(original.review.makeup, "Makeup", filename))
        
        if original.review.costumes != "":
            review.costumes.MergeFrom(convert_generic(original.review.costumes, "Costumes", filename))
        
        if original.review.plot_structure != "":
            review.plot_structure = original.review.plot_structure
        
        if original.review.pacing != "":
            review.pacing = original.review.pacing
        
        if original.review.climax != "":
            review.climax = original.review.climax
        
        if original.review.tone != "":
            review.tone = original.review.tone
        
        review.final_notes = original.review.final_notes
        
        if original.review.overall != "":
            review.overall = original.review.overall

        return movie_pb2.Movie(title = original.title, rating = original.rating, review = review, release_year = original.release_year, review_date = original.review_date, redux = original.redux, id = original.id, imdb_id = original.imdb_id)

    except ValueError as e:
        print(e)


# Helper Functions
def closes_all_brackets(comments, filename):
    start = comments.find("(")
    if start == -1:
        return True

    if comments[-1] != ")":
        raise ValueError("Issue with {}: Field should end with a closing parenthesis. Field is \"{}\".".format(filename, comments))
    try:
        current = start + 1

        stack = []
        while current < len(comments) - 1:
            if comments[current] == "(":
                stack.append("(")
            elif comments[current] == ")":
                stack.pop()
            current += 1
    except IndexError:
        raise ValueError("Issue with {}: Bracket mismatch. Field is \"{}\".".format(filename, comments))
    
    return len(stack) == 0

def split(field, delimiter):
    rating, comments = field.split(delimiter, 1)
    return rating.strip(), "{} {}".format(delimiter.strip(), comments.strip())

def clean_comments(comments, filename):
    if closes_all_brackets(comments, filename):
        start = comments.find("(")
        if start == -1:
            return ""
        else:
            return comments[start + 1:-1]
    else:
        raise ValueError("Issue with {}: There is a bracket mismatch in \"{}\"".format(filename, comments))
    
def get_rating_and_comments(field, splitter, filename):
    rating, comments = split(field, splitter)
    comments = clean_comments(comments, filename)
    return rating, comments

def get_rating_and_comments_generic(field, splitter, filename):
    rating, comments = split(field, splitter)
    comments = clean_comments(comments, filename)
    return rating, comments

def field_name_error_check(field_name, field, filename):
    if field_name not in field:
        raise ValueError("Issue with {}: problem with \"{}\"".format(filename, field_name))

def missing_tier(field, field_name, filename):
    if field.startswith(field_name):
        raise ValueError("Issue with {}: \"{}\" does not have a tier".format(filename, field_name))

def read_old_format(filename):
    with open("movies_textproto/" + filename + ".textproto", "r") as fd:
        text_proto = fd.read()
        
        fd.seek(0)
        if len(fd.readlines()) <= 8:
            return text_format.Parse(text_proto, movie_pb2.MovieFree())
        else: 
            try:
                # return text_format.Parse(text_proto, movie_pb2.MovieOldFormat())
                return text_format.Parse(text_proto, movie_pb2.Movie())
            except:
                raise ValueError ("{} is the new format, skipping".format(filename))