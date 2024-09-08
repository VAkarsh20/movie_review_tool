GEMINI_REQUEST_LIMIT = 10
GEMINI_PROMPT = "Proofread (focus on spelling and grammar, do not provide any explantation, do not use a semi-colon in grammar fixes, replace the end of each sentence with a ';', the last sentence should not end with any punctuation)"

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
    0.5: (1.0, 2.0),
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
    1: (1.0, 2.0),
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

# IMDB XPATHs
IMDB_STARS_ELEMENTS_CLASS_NAME = "ice-star-wrapper"
IMDB_HEADLINE_ELEMENT_XPATH = "/html/body/div[1]/div/div/div/div[1]/div[5]/div[1]/input"
IMDB_REVIEW_ELEMENT_XPATH = (
    "/html/body/div[1]/div/div/div/div[1]/div[5]/div[2]/textarea"
)
IMDB_NO_SPOLIERS_ELEMENT_XPATH = (
    "/html/body/div[1]/div/div/div/div[1]/div[5]/div[3]/div/ul/li[2]"
)
IMDB_SUBMIT_ELEMENT_XPATH = "/html/body/div[1]/div/div/div/div[2]/span/span/input"
IMDB_ADD_TO_LIST_SEARCH_ELEMENT_XPATH = '//*[@id="add-to-list-search"]'
IMDB_FIRST_MOVIE_IN_SEARCH_ELEMENT_XPATH = (
    "/html/body/div[2]/div/div[2]/div[3]/div[1]/div[2]/div[5]/div/span[2]/div/a"
)
IMDB_SAVE_LIST_ELEMENT_XPATH = (
    "/html/body/div[2]/div/div[2]/div[3]/div[1]/div[1]/button"
)

# IMDB URLs
IMDB_HOME_PAGE_URL = "https://www.imdb.com/"
IMDB_MOVIE_PAGE_URL = "https://www.imdb.com/title/{}"
IMDB_ADD_MOVIE_REVIEW_PAGE_URL = "https://contribute.imdb.com/review/{}/add?"
IMDB_CINEMA_PERSONIFIED_LIST_URL = (
    "https://www.imdb.com/list/ls520163773/edit?ref_=ttls_edt"
)

# Letterboxd File Strings
LETTERBOXD_UPLOAD_CSV = "letterboxd_upload.csv"
LETTERBOXD_UPLOAD_FILE = "letterboxd_upload_file"
LETTERBOXD_COOKIES_PKL = "letterboxd_cookies.pkl"
LETTERBOXD_DOMAIN = ".letterboxd.com"

# Letterboxd UI Strings
LETTERBOXD_ADD_FILM_TO_LISTS = "Add this film to lists…"
LETTERBOXD_LIKE = "Like"

# Letterboxd URLs
LETTERBOXD_HOME_PAGE_URL = "https://letterboxd.com/"
LETTERBOXD_IMPORT_PAGE_URL = "https://letterboxd.com/import/"
LETTERBOXD_USER_PAGE_URL = "https://letterboxd.com/akarshv/"

# Letterboxd XPATHs
LETTERBOXD_SIGN_IN_ELEMENT_XPATH = "/html/body/div[1]/div/form/div/div[3]/button"
LETTERBOXD_UPLOAD_IMDB_IMPORT_ELEMENT_ID = "upload-imdb-import"
LETTERBOXD_SUBMIT_REVIEW_ELEMENT_XPATH = '//*[@id="content"]/div/div[1]/a[2]'
LETTERBOXD_MOVIE_IMAGE_ELEMENT = "link text"
LETTERBOXD_LIKE_TEXT_ELEMENT_XPATH = (
    '//*[@id="userpanel"]/ul/li[1]/span[2]/span/span/span'
)
LETTERBOXD_LIKE_BUTTON_ELEMENT_XPATH = (
    "/html/body/div[2]/div/div/aside/section[1]/ul/li[1]/span[2]/span/span/span"
)
LETTERBOXD_CINEMA_PERSONIFIED_LIST_ELEMENT_XPATH = (
    "/html/body/div[6]/div[1]/div[2]/div[2]/div[1]/div/form/div[2]/div[1]/label"
)
LETTERBOXD_ADD_TO_LIST_ELEMENT_XPATH = (
    '//*[@id="add-to-a-list-modal"]/form/div[3]/div[2]/input'
)
