from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import protos.movie_pb2
from utils.rating_utils import *
from utils.date_utils import change_date_format
from utils.constants import *
from utils.selenium_utils import load_cookies, exception_handler
from utils.flags import LOGIN_WITH_COOKIES
import pandas as pd
import yaml
import pickle
import os
import time

# export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}'):0.0
# LIBGL_ALWAYS_INDIRECT=1

# TODO: See why You always have to run this file twice cause there is this error - OSError: [Errno 26] Text file busy: '/home/akarsh/.wdm/drivers/geckodriver/linux64/0.33/geckodriver'
# TODO: EOFError: Compressed file ended before the end-of-stream marker was reached
# TODO: Issues when clicking Import File 
# Stacktrace:
# RemoteError@chrome://remote/content/shared/RemoteError.sys.mjs:8:8
class LetterboxdBot:
    def __init__(self):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def wait(self, seconds):
        self.driver.maximize_window()
        self.driver.implicitly_wait(seconds)

    def login(self):
        # Getting home page
        try:
            self.driver.get(LETTERBOXD_IMPORT_PAGE_URL)
        except Exception as e:
            exception_handler("Exception thrown when getting letterboxd import page: {}".format(e))

        if LOGIN_WITH_COOKIES:
            self.driver = load_cookies(self.driver, LETTERBOXD_COOKIES_PKL, LETTERBOXD_DOMAIN)
            time.sleep(10)
        else:
            yml = yaml.safe_load(open('login_details.yml'))['letterboxd']

            # Logging in
            try:
                self.wait(15)
                self.driver.find_element(By.NAME, "username").send_keys(yml['username'])
                self.driver.find_element(By.NAME, "password").send_keys(yml['password'])
                self.driver.find_element(By.XPATH,LETTERBOXD_SIGN_IN_ELEMENT_XPATH).click()
            except Exception as e:
                exception_handler("Exception thrown when logging in: {}".format(e))
    
    def import_review(self):
        # Getting import page
        try:
            self.wait(15)
            self.driver.get(LETTERBOXD_IMPORT_PAGE_URL)
        except Exception as e:
            exception_handler("Exception thrown when getting import page: {}".format(e))
        
        # Uploading letterboxd csv
        try:
            self.wait(10)
            file = yaml.safe_load(open('local_filepaths.yml'))[LETTERBOXD_UPLOAD_FILE]["filepath"]
            self.driver.find_element(By.ID, LETTERBOXD_UPLOAD_IMDB_IMPORT_ELEMENT_ID).send_keys(file)
        except Exception as e:
            exception_handler("Exception thrown when uploading letterboxd csv: {}".format(e))
        
        # Submitting review
        try:
            self.wait(45)
            self.driver.find_element(By.XPATH, LETTERBOXD_SUBMIT_REVIEW_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when submitting review: {}".format(e))

    # TODO: Edge Case, movie that was originally a like but after redux is not
    def liked_film(self, title):
        try:
            self.wait(10)
            self.driver.get(LETTERBOXD_USER_PAGE_URL)
        except Exception as e:
            exception_handler("Exception thrown when getting user page: {}".format(e))

        try:
            self.wait(10)
            self.driver.find_element(LETTERBOXD_MOVIE_IMAGE_ELEMENT, title).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking movie: {}".format(e))

        try:
            self.wait(10)
            if self.driver.find_element(By.XPATH, LETTERBOXD_LIKE_TEXT_ELEMENT_XPATH).text == LETTERBOXD_LIKE:
                self.driver.find_element(By.XPATH, LETTERBOXD_LIKE_BUTTON_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when liking movie: {}".format(e))
    
    # TODO: Check if film is already in the list
    def add_to_cinema_personified_list(self):
        try:
            self.wait(10)
            self.driver.find_element(LETTERBOXD_MOVIE_IMAGE_ELEMENT, LETTERBOXD_ADD_FILM_TO_LISTS).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking add film to list: {}".format(e))

        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, LETTERBOXD_CINEMA_PERSONIFIED_LIST_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking Cinema Personified list: {}".format(e))

        try:
            self.wait(10)
            self.driver.find_element(By.XPATH, LETTERBOXD_ADD_TO_LIST_ELEMENT_XPATH).click()
        except Exception as e:
            exception_handler("Exception thrown when clicking add: {}".format(e))
        
    def quit(self):
        self.driver.quit()

def create_letterboxd_csv(proto, short_review):
    df = pd.DataFrame(columns=["imdbID", "Title", "Year", "Rating","WatchedDate","Tags","Review"])

    record = [proto.imdb_id, proto.title, proto.release_year, rating_to_stars(proto.rating), change_date_format(proto.review_date), rating_to_tag(proto.rating), short_review]
    df.loc[1] = record

    df.to_csv(LETTERBOXD_UPLOAD_CSV, index=False)

def post_to_letterboxd(proto, short_review):
    create_letterboxd_csv(proto, short_review)

    letterboxd_bot = LetterboxdBot()

    letterboxd_bot.login()
    letterboxd_bot.import_review()

    if proto.rating >= 8.5:
        letterboxd_bot.liked_film(proto.title)

    if proto.rating >= 9.5:
        letterboxd_bot.add_to_cinema_personified_list()
    
    os.remove(LETTERBOXD_UPLOAD_CSV)


    # TODO: Stuck on There was an OSError: [Errno 2] No such file or directory: 'letterboxd_upload.csv' after done.
    # tries = 5
    # import_check, liked_check, list_check = False, False, False
    # while tries > 0:
    #     try:
    #         if not import_check:
    #             letterboxd_bot.login(username, password)
    #             letterboxd_bot.import_review()
    #             import_check = True

    #         if proto.rating >= 8.5 and not liked_check:
    #             letterboxd_bot.liked_film(proto.title)
    #             liked_check = True
    #         os.remove("letterboxd_upload.csv")

    #         if proto.rating >= 9.5 and not list_check:
    #             letterboxd_bot.add_to_cinema_personified_list()
    #             list_check = True
    #     except OSError as e:
    #         print("There was an OSError: {}".format(e))
    #         time.sleep(3)
    #     except EOFError as e:
    #         print("There was an EOFError: {}".format(e))

    letterboxd_bot.quit()





