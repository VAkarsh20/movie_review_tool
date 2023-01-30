from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import movie_pb2

class LetterboxdBot:
    def __init__(self):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def wait(self):
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

    def login(self, username, password):
        
        self.driver.get("https://letterboxd.com/sign-in/")

        self.wait()

        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.XPATH,"/html/body/div[1]/div/div/form/fieldset/div[4]/div/input").click()

    def log_film(self, proto):

        self.wait()

        log_button = self.driver.find_element(By.XPATH,'//*[@id="add-new-button"]').click()

        self.wait()

        search = "{} ({})".format(proto.title, proto.release_year)

        self.driver.find_element(By.ID,'frm-film-name').send_keys(search)

        self.wait()

        self.driver.find_element(By.XPATH,'/html/body/div[12]/ul').click()

        self.liked_film(proto.rating)

        self.write_review(proto.rating, proto.review.overall) 

        self.add_tag(proto.rating)

    def liked_film(self, rating):
        if rating >= 8.5:
            self.wait()
            self.driver.find_element(By.XPATH, '//*[@id="film-like-checkbox"]').click()

    def write_review(self, rating, overall):

        self.wait()
        review = "Rating: {}/10.0\n\n{}.".format(rating, overall)
        self.driver.find_element(By.XPATH,'//*[@id="frm-review"]').send_keys(review)
    
    def rating_to_tag(self, rating):

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
        elif rating in range(75, 80):
            return "Pretty Good"
        elif rating in range(70, 75):
            return "Decent"
        elif rating in range(60, 70):
            return "Pretty Bad"
        elif rating in range(50, 60):
            return "Bad"
        elif rating in range(40, 50):
            return "Very Bad"
        else:
            return "Terrible"
    
    def add_tag(self, rating):
        
        self.wait()
        tag = self.rating_to_tag(rating)
        self.driver.find_element(By.XPATH,'//*[@id="frm-tags"]').send_keys(tag)
        


# driver.implicitly_wait(10)


# 

# driver.implicitly_wait(10)

# driver.find_element(By.XPATH,'//*[@id="rateit-range-2"]').setAttribute("aria-valuenow", "8")
# stars = driver.find_element(By.XPATH,'//*[@id="rateit-range-2"]')
# actions = ActionChains(driver)
# actions.key_up("38", stars)
# actions.perform()

# driver.find_element(By.XPATH, '/html/body/div[6]/div[1]/div[2]/div[2]/div[1]/div/article/section[2]/form/fieldset/div[3]/div[3]/div').send_keys("8")

# driver.find_element(By.XPATH,'//*[@id="rateit-range-2"]').send_keys("aria-valuenow","8")

# driver.find_element(By.XPATH,'//*[@id="rateit-range-2"]').mouseover






