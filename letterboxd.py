from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import movie_pb2
import pandas as pd
import yaml
import os

# export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}'):0.0
# LIBGL_ALWAYS_INDIRECT=1

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
        
        self.wait(30)
        self.driver.find_element(By.XPATH,"/html/body/div[2]/div/div[1]/a[2]").click()

    # TODO: Fix Bug where it removes like
    def liked_film(self, title):
        
        self.wait(10)
        self.driver.get("https://letterboxd.com/akarshv/")

        self.wait(10)
        self.driver.find_element("link text", title).click()

        self.wait(10)
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


def rating_to_stars(rating):

    rating = int (rating * 10)

    # Mapping rating to its respective star
    if rating in range(95, 100):
        return 5
    elif rating in range(90, 95):
        return 4.5
    elif rating in range(80, 90):
        return 4
    elif rating in range(70, 78):
        return 3.5
    elif rating in range(60, 70):
        return 3
    elif rating in range(50, 60):
        return 2.5
    elif rating in range(40, 50):
        return 2.0
    elif rating in range(30, 40):
        return 1.5
    elif rating in range(20, 30):
        return 1.0
    elif rating in range(10, 20):
        return 0.5
    else:
        return 0

def rating_to_tag(rating):

    rating = int (rating * 10)

    # Mapping rating to its respective tag
    if rating in range(97, 100):
        return "Brilliant"
    elif rating in range(95, 97):
        return "Incredible"
    elif rating in range(90, 95):
        return "Great"
    elif rating in range(85, 90):
        return "Very Good"
    elif rating in range(80, 85):
        return "Good"
    elif rating in range(70, 80):
        return "Pretty Good"
    elif rating in range(60, 70):
        return "Decent"
    elif rating in range(50, 60):
        return "Pretty Bad"
    elif rating in range(40, 50):
        return "Bad"
    elif rating in range(30, 40):
        return "Very Bad"
    else:
        return "Terrible"

def change_date_format(date):
    month, day, year = date.split("/")
    return "{}-{}-{}".format(year, month, day)

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

    letterboxd_bot.quit()





