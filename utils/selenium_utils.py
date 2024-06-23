import pickle

def load_cookies(driver, filename, domain):
    cookies = pickle.load(open(filename, "rb"))

    for cookie in cookies:
        cookie['domain'] = domain
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(e)
    return driver

def exception_handler(message):
    print(message)
    time.sleep(20)