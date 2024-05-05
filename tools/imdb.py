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

class IMDbBot:
    def __init__(self):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def wait(self, seconds):
        self.driver.maximize_window()
        self.driver.implicitly_wait(seconds)

    def load_cookies(self):
        cookies = pickle.load(open("imdb_cookies.pkl", "rb"))

        for cookie in tqdm.tqdm(cookies):
            cookie['domain'] = ".imdb.com"
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(e)

    def login(self):
        
        self.driver.get("https://www.imdb.com/")

        self.load_cookies()
    
    def import_review(self, imdb_id, rating, review):

        self.wait(5)
        self.driver.get("https://contribute.imdb.com/review/{}/add?".format(imdb_id))

        self.wait(10)
        stars = self.driver.find_elements(By.CLASS_NAME, "ice-star-wrapper")
        imdb_rating = rating_to_imdb_score(rating)
        stars[imdb_rating - 1].click()

        self.wait(10)
        title = "{} Movie".format(rating_to_tag(rating))
        if rating >= 9.5:
            title = "Cinema Personified: " + title
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div[5]/div[1]/input').clear()
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div[5]/div[1]/input').send_keys(title)

        self.wait(10)
        self.driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div/div[1]/div[5]/div[2]/textarea').clear()
        self.driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div/div[1]/div[5]/div[2]/textarea').send_keys(review)

        self.wait(10)
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div[5]/div[3]/div/ul/li[2]').click()

        self.wait(10)
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[2]/span/span/input').click()

        self.wait(10)
        self.driver.get("https://www.imdb.com/title/{}".format(imdb_id))
    
    # TODO: Check if film is already in the list
    def add_to_cinema_personified_list(self, imdb_id, title, year):
        
        self.wait(10)
        self.driver.get("https://www.imdb.com/list/ls520163773/edit?ref_=ttls_edt")
        self.driver.find_element(By.XPATH, '//*[@id="add-to-list-search"]').send_keys("{} {} ({})".format(imdb_id, title, year))

        self.wait(10)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[3]/div[1]/div[2]/div[5]/div/span[2]/div/a").click()

        self.wait(10)
        self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/div[1]/div[1]/button').click()

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





