from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import protos.movie_pb2
from utils.rating_utils import *
from utils.date_utils import change_date_format
import pandas as pd
import yaml
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

    def login(self, username, password):
        self.driver.get("https://letterboxd.com/import/")

        self.wait(15)
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.XPATH,"/html/body/div[1]/div/form/div/div[3]/button").click()
    
    def import_review(self):
        self.wait(15)
        self.driver.find_element(By.ID, "upload-imdb-import").send_keys("/mnt/c/Users/vakar/personal-repos/movies/movie_review_tool/letterboxd_upload.csv")
        
        self.wait(45)
        self.driver.find_element(By.XPATH,'//*[@id="content"]/div/div[1]/a[2]').click()

    # TODO: Edge Case, movie that was originally a like but after redux is not
    def liked_film(self, title):
        self.wait(10)
        self.driver.get("https://letterboxd.com/akarshv/")

        self.wait(10)
        self.driver.find_element("link text", title).click()

        self.wait(10)
        if self.driver.find_element(By.XPATH, '//*[@id="userpanel"]/ul/li[1]/span[2]/span/span/span').text == "Like":
            self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/aside/section[1]/ul/li[1]/span[2]/span/span/span").click()

        # Deprecated way
        # self.wait(10)
        # self.driver.find_element("link text", "Edit or delete this review…").click()

        # self.wait(10)
        # self.driver.find_element(By.XPATH, '//*[@id="film-like-checkbox"]').click()

        # self.wait(10)
        # self.driver.find_element(By.XPATH, '//*[@id="diary-entry-submit-button"]').click()
    
    # TODO: Check if film is already in the list
    def add_to_cinema_personified_list(self):
        self.wait(10)
        self.driver.find_element("link text", "Add this film to lists…").click()

        self.wait(10)
        self.driver.find_element(By.XPATH, '/html/body/div[6]/div[1]/div[2]/div[2]/div[1]/div/form/div[2]/div[1]/label').click()

        self.wait(10)
        self.driver.find_element(By.XPATH, '//*[@id="add-to-a-list-modal"]/form/div[3]/div[2]/input').click()
        
    def quit(self):
        self.driver.quit()

def create_letterboxd_csv(proto, short_review):
    df = pd.DataFrame(columns=["imdbID", "Title", "Year", "Rating","WatchedDate","Tags","Review"])

    record = [proto.imdb_id, proto.title, proto.release_year, rating_to_stars(proto.rating), change_date_format(proto.review_date), rating_to_tag(proto.rating), short_review]
    df.loc[1] = record

    df.to_csv("letterboxd_upload.csv", index=False)

def post_to_letterboxd(proto, short_review):
    yml = yaml.safe_load(open('login_details.yml'))
    username = yml['letterboxd']['username']
    password = yml['letterboxd']['password']

    create_letterboxd_csv(proto, short_review)

    letterboxd_bot = LetterboxdBot()

    letterboxd_bot.login(username, password)
    letterboxd_bot.import_review()

    if proto.rating >= 8.5:
        letterboxd_bot.liked_film(proto.title)
    os.remove("letterboxd_upload.csv")

    if proto.rating >= 9.5:
        letterboxd_bot.add_to_cinema_personified_list()


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





