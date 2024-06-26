from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from protos import movie_pb2
import pandas as pd
import yaml
import os
import undetected_chromedriver as uc
import time
import pickle

class RottenTomatoesBot:
    def __init__(self):
        self.driver = uc.Chrome()


    def load_cookies(self):
        cookies = pickle.load(open("rotten_tomatoes_cookies.pkl", "rb"))

        for cookie in cookies:
            cookie['domain'] = ".rottentomatoes.com"
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(e)


    def wait(self, seconds):
        self.driver.maximize_window()
        self.driver.implicitly_wait(seconds)


    def login(self):
        
        self.driver.get("https://www.rottentomatoes.com/")
        self.wait(10)
        # pickle.dump(self.driver.get_cookies(), open("rotten_tomatoes_cookies.pkl", "wb"))
        self.load_cookies()

    def import_review(self, short_review):
        
        self.wait(10)
        self.driver.get("https://www.rottentomatoes.com/m/mean_girls")
        self.wait(10)
        self.driver.find_element(By.XPATH, '//*[@id="rating-widget-desktop"]/div/section/div[2]/div[1]/div[1]/span/span[4]/span[2]').click()
        self.wait(20)
        self.driver.find_element(By.XPATH, '//*[@id="rating-root"]/aside[1]/div/div/div[2]/div/div/textarea').send_keys(short_review)
        self.wait(20)
        self.driver.find_element(By.XPATH, '/html/body/div[3]/main/div[1]/section/div[2]/section[1]/div[3]/div/div[2]/aside[1]/div/div/div[3]/button').click()
        time.sleep(30)
        self.driver.get("https://www.rottentomatoes.com/m/mean_girls")
        time.sleep(60)
        # 
        # 
#         self.wait(15)
#         self.driver.find_element(By.ID, "upload-imdb-import").send_keys("/mnt/c/Users/vakar/personal-repos/movies/movie_review_tool/letterboxd_upload.csv")
        
#         self.wait(30)
#         self.driver.find_element(By.XPATH,"/html/body/div[2]/div/div[1]/a[2]").click()
        

        

#         self.wait(10)
#         self.driver.find_element(By.NAME, "username").send_keys(username)
#         self.driver.find_element(By.NAME, "password").send_keys(password)
#         self.driver.find_element(By.XPATH,"/html/body/div[1]/div/div/form/fieldset/div[4]/div/input").click()
    
#     def import_review(self):
        
#         self.wait(15)
#         self.driver.find_element(By.ID, "upload-imdb-import").send_keys("/mnt/c/Users/vakar/personal-repos/movies/movie_review_tool/letterboxd_upload.csv")
        
#         self.wait(30)
#         self.driver.find_element(By.XPATH,"/html/body/div[2]/div/div[1]/a[2]").click()

#     def liked_film(self, title):
        
#         self.wait(10)
#         self.driver.get("https://letterboxd.com/akarshv/")

#         self.wait(10)
#         self.driver.find_element("link text", title).click()

#         self.wait(10)
#         self.driver.find_element("link text", "Edit or delete this review…").click()

#         self.wait(10)
#         self.driver.find_element(By.XPATH, '//*[@id="film-like-checkbox"]').click()

#         self.wait(10)
#         self.driver.find_element(By.XPATH, '//*[@id="diary-entry-submit-button"]').click()
#     def quit(self):
#         self.driver.quit()

# def change_date_format(date):
#     month, day, year = date.split("/")
#     return "{}-{}-{}".format(year, month, day)

# def create_letterboxd_csv(proto, short_review):
    
#     df = pd.DataFrame(columns=["imdbID", "Title", "Year", "Rating","WatchedDate","Tags","Review"])

#     record = [proto.imdb_id, proto.title, proto.release_year, rating_to_stars(proto.rating), change_date_format(proto.review_date), rating_to_tag(proto.rating), short_review]
#     df.loc[1] = record

#     df.to_csv("letterboxd_upload.csv", index=False)

# def post_to_letterboxd(proto, short_review):
    
#     yml = yaml.safe_load(open('login_details.yml'))
#     username = yml['letterboxd']['username']
#     password = yml['letterboxd']['password']

#     create_letterboxd_csv(proto, short_review)

#     letterboxd_bot = LetterboxdBot()
#     letterboxd_bot.login(username, password)
#     letterboxd_bot.import_review()

#     if proto.rating >= 8.5:
#         letterboxd_bot.liked_film(proto.title)
#     os.remove("letterboxd_upload.csv")

#     letterboxd_bot.quit()





