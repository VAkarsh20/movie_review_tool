from utils.constants import stars_ratings_dict, imdb_ratings_dict, tags_ratings_dict

def rating_to_stars(rating):
    rating = int (rating * 10)
    for star, rating_range in stars_ratings_dict.items():
        if rating > 99:
            raise ValueError("Rating needs to be between [1.0, 10.0)")

        if rating in range(int(rating_range[0] * 10), int(rating_range[1] * 10)):
            return star
    return 0

def rating_to_tag(rating):
    rating = int (rating * 10)
    for tag, rating_range in tags_ratings_dict.items():
        if rating > 99:
            raise ValueError("Rating needs to be between [1.0, 10.0)")
        
        if rating in range(int(rating_range[0] * 10), int(rating_range[1] * 10)):
            return tag
    return "Terrible"

def rating_to_imdb_score(rating):
    rating = int (rating * 10)
    for imdb_score, rating_range in imdb_ratings_dict.items():
        if rating > 99:
            raise ValueError("Rating needs to be between [1.0, 10.0)")
        
        if rating in range(int(rating_range[0] * 10), int(rating_range[1] * 10)):
            return imdb_score
    return 0