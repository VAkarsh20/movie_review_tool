from utils.constants import stars_ratings_dict, tags_ratings_dict

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

    # # Mapping rating to its respective tag
    # if rating in range(97, 100):
    #     return "Brilliant"
    # elif rating in range(95, 97):
    #     return "Incredible"
    # elif rating in range(90, 95):
    #     return "Great"
    # elif rating in range(85, 90):
    #     return "Very Good"
    # elif rating in range(80, 85):
    #     return "Good"
    # elif rating in range(70, 80):
    #     return "Pretty Good"
    # elif rating in range(60, 70):
    #     return "Decent"
    # elif rating in range(50, 60):
    #     return "Pretty Bad"
    # elif rating in range(40, 50):
    #     return "Bad"
    # elif rating in range(30, 40):
    #     return "Very Bad"
    # else:
    #     return "Terrible"