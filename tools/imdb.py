from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.rating_utils import rating_to_tag, rating_to_imdb_score
import protos.movie_pb2
import pandas as pd
import yaml
import os
import requests
import pickle
import tqdm
from google.protobuf import text_format
import time
from utils.constants import *
from utils.selenium_utils import load_cookies, exception_handler

class IMDbBot:
    def __init__(self):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def wait(self, seconds):
        self.driver.maximize_window()
        self.driver.implicitly_wait(seconds)

    def login(self):
        self.driver.get(IMDB_HOME_PAGE_URL)
        self.driver = load_cookies(self.driver, "imdb_cookies.pkl", ".imdb.com")
        time.sleep(5)

    
    def import_review(self, imdb_id, rating, review):

        # Getting review page
        try:
            self.wait(5)
            self.driver.get(IMDB_ADD_MOVIE_REVIEW_PAGE_URL.format(imdb_id))
        except Exception as e:
            exception_handler("Exception thrown when getting review page: {}".format(e))

        # Clicking stars
        imdb_rating = rating_to_imdb_score(rating)
        try:
            self.wait(10)
            stars = self.driver.find_elements(By.CLASS_NAME, IMDB_STARS_ELEMENTS_CLASS_NAME)
        except Exception as e:
            exception_handler("Exception thrown when finding stars element: {}".format(e))
        try:    
            stars[imdb_rating - 1].click()
        except ValueError as e:
            exception_handler("ValueError thrown when trying to click stars: {}".format(e))

        # Sending headline
        title = "{} Movie".format(rating_to_tag(rating))
        if rating >= 9.5:
            title = "Cinema Personified: " + title
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, IMDB_HEADLINE_ELEMENT_XPATH).clear()
            self.driver.find_element(By.XPATH, IMDB_HEADLINE_ELEMENT_XPATH).send_keys(title)
        except Exception as e:
            exception_handler("Exception thrown when accessing headline element: {}".format(e))

        # Sending review
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH,IMDB_REVIEW_ELEMENT_XPATH).clear()
            self.driver.find_element(By.XPATH,IMDB_REVIEW_ELEMENT_XPATH).send_keys(review)
        except Exception as e:
            exception_handler("Exception thrown when accessing review element: {}".format(e))

        # Spoilers
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, IMDB_NO_SPOLIERS_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking spoiler element: {}".format(e))

        # Submit
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, IMDB_SUBMIT_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking submit element: {}".format(e))

        # Get movie imdb page
        try:
            self.wait(10)
            self.driver.get(IMDB_MOVIE_PAGE_URL.format(imdb_id))
        except Exception as e:
            exception_handler("Exception thrown when getting imdb movie page: {}".format(e))
    
    # TODO: Check if film is already in the list
    def add_to_cinema_personified_list(self, imdb_id, title, year):

        # Getting Cinema Personified list page
        try:
            self.wait(10)
            self.driver.get(IMDB_CINEMA_PERSONIFIED_LIST_URL)
        except Exception as e:
            exception_handler("Exception thrown when getting cinema personified list: {}".format(e))
        
        # Searching for movie
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, IMDB_ADD_TO_LIST_SEARCH_ELEMENT_XPATH).send_keys("{} {} ({})".format(imdb_id, title, year))
        except Exception as e:
            exception_handler("Exception thrown when sending keys to add to list search: {}".format(e))

        # Clicking movie
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, IMDB_FIRST_MOVIE_IN_SEARCH_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking movie in list search: {}".format(e))

        # Saving list
        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, IMDB_SAVE_LIST_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when saving movie in Cinema Personified list: {}".format(e))

        self.wait(15)
        
    def quit(self):
        self.driver.quit()

def post_to_imdb(proto, review):
    bot = IMDbBot()
    bot.login()
    bot.import_review(proto.imdb_id, proto.rating, review)
    if proto.rating >= 9.5:        
        bot.add_to_cinema_personified_list(proto.imdb_id, proto.title, proto.release_year)
    bot.quit()

# inspired from https://github.com/TobiasPankner/Letterboxd-to-IMDb/blob/master/letterboxd2imdb.py
def rate_on_imdb(imdb_id, rating):
    
    # global imdb_cookie
    # with open('cookie.txt', 'r', encoding='latin-1') as file:
    #     imdb_cookie = file.read().replace('\n', '').strip()
    
    req_body = {
        "query": "mutation UpdateTitleRating($rating: Int!, $titleId: ID!) { rateTitle(input: {rating: $rating, titleId: $titleId}) { rating { value __typename } __typename }}",
        "operationName": "UpdateTitleRating",
        "variables": {
            "rating": rating,
            "titleId": imdb_id
        }
    }
    headers = {
        "content-type": "application/json",
        "cookie": imdb_cookie
    }

    resp = requests.post("https://api.graphql.imdb.com/", json=req_body, headers=headers)

    if resp.status_code != 200:
        if resp.status_code == 429:
            raise RateLimitError("IMDb Rate limit exceeded")
        raise ValueError(f"Error rating on IMDb. Code: {resp.status_code}")

    json_resp = resp.json()
    if 'errors' in json_resp and len(json_resp['errors']) > 0:
        first_error_msg = json_resp['errors'][0]['message']

        if 'Authentication' in first_error_msg:
            print(f"Failed to authenticate with cookie")
            exit(1)
        else:
            raise ValueError(first_error_msg)





