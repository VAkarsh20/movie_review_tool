# Mapping rating to its respective star
# Each range is as follows: [Start, End)
stars_ratings_dict = {
    5.0: (9.5, 10.0),
    4.5: (9.0, 9.5),
    4.0: (8.0, 9.0),
    3.5: (7.0, 8.0),
    3.0: (6.0, 7.0),
    2.5: (5.0, 6.0),
    2.0: (4.0, 5.0),
    1.5: (3.0, 4.0),
    1.0: (2.0, 3.0),
    0.5: (1.0, 2.0)
}

# Mapping rating to its respective IMDb rating
# Each range is as follows: [Start, End)
imdb_ratings_dict = {
    10: (9.5, 10.0),
    9: (9.0, 9.5),
    8: (8.0, 9.0),
    7: (7.0, 8.0),
    6: (6.0, 7.0),
    5: (5.0, 6.0),
    4: (4.0, 5.0),
    3: (3.0, 4.0),
    2: (2.0, 3.0),
    1: (1.0, 2.0)
}

# Mapping rating to its respective tag
# Each range is as follows: [Start, End)
tags_ratings_dict = {
    "Brilliant": (9.7, 10.0),
    "Incredible": (9.5, 9.7),
    "Great": (9.0, 9.5),
    "Very Good": (8.5, 9.0),
    "Good": (8.0, 8.5),
    "Pretty Good": (7.0, 8.0),
    "Decent": (6.0, 7.0),
    "Pretty Bad": (5.0, 6.0),
    "Bad": (4.0, 5.0),
    "Very Bad": (3.0, 4.0),
    "Terrible": (1.0, 3.0),
}