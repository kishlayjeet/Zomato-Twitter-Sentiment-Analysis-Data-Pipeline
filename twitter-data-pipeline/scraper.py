import time
import random
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC


# Setup logging
logging.basicConfig(level=logging.INFO)

# Twitter CSS selectors
ARTICLE_CSS = "article.css-1dbjc4n.r-1loqt21.r-18u37iz.r-1ny4l3l.r-1udh08x.r-1qhn6m8.r-i023vh.r-o7ynqc.r-6416eg"
USER_CSS = ".css-1dbjc4n.r-1awozwy.r-18u37iz.r-1wbh5a2.r-dnmrzs"
USERNAME_CSS = ".css-1dbjc4n.r-18u37iz.r-1wbh5a2.r-13hce6t"
TEXT_CSS = ".css-901oao.r-1nao33i.r-37j5jr.r-a023e6.r-16dba41.r-rjixqe.r-bcqeeo.r-bnwqim.r-qvutc0"
DATE_CSS = ".css-1dbjc4n.r-18u37iz.r-1wbh5a2.r-13hce6t"
COUNT_CSS = ".css-1dbjc4n.r-1kbdv8c.r-18u37iz.r-1wtj0ep.r-1s2bzr4.r-hzcoqn"


class TwitterScraper:
    def __init__(self, query, auth_token, width=1920, height=1080):
        self.query = query
        self.auth_token = auth_token
        self.width = width
        self.height = height
        self.df = None
        self.driver = None
        self.file_name = None
        self.create_driver()
        
    def create_driver(self):
        """Initializes the selenium webdriver."""
        try:
            options = Options()
            options.add_argument('--blink-settings=imagesEnabled=false')
            # options.add_argument('--headless')
            
            # Setting a common user-agent
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537")
            
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(self.width, self.height)
            self.driver = driver
            logging.info("WebDriver initialized successfully.")
        except Exception as e:
            logging.error("WebDriver failed to initialize.")            
            self.driver = None
            raise e

    def login_and_search(self):
        """Login into Twitter and performs search."""
        twitter_url = 'https://twitter.com/'
        twitter_search_url = f'https://twitter.com/search?q={self.query}&src=typed_query&f=live'

        try:
            self.driver.get(twitter_url)
            self.driver.add_cookie({
                'name': 'auth_token',
                'value': self.auth_token
            })
            self.driver.get(twitter_search_url)
            WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ARTICLE_CSS)))
        except TimeoutException:
            logging.error(f"Timed out waiting for element with selector {ARTICLE_CSS}.")
            raise
        except Exception as e:
            logging.error(
                f"Error occurred while logging into Twitter and performing the search.")
            self.driver.quit()
            self.driver = None
            raise e

    def scrap_tweets(self):
        """Scrapes tweets from the page."""
        tweets_data = []
        try:
            article_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ARTICLE_CSS)
            for article in article_elements:
                tweet_data = {}
                try:
                    user = article.find_element(By.CSS_SELECTOR, USER_CSS).find_element(
                        By.CSS_SELECTOR, ".css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0").text.strip()
                    tweet_data['user'] = user
                except NoSuchElementException:
                    pass
                try:
                    username = article.find_element(By.CSS_SELECTOR, USERNAME_CSS).find_element(
                        By.CSS_SELECTOR, ".css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0").text.strip()
                    tweet_data['username'] = username
                except NoSuchElementException:
                    pass
                try:
                    text = article.find_element(
                        By.CSS_SELECTOR, TEXT_CSS).text.strip().replace('\n', '')
                    tweet_data['text'] = text
                except NoSuchElementException:
                    pass
                try:
                    date_and_time = article.find_element(By.CSS_SELECTOR, DATE_CSS).find_element(
                        By.TAG_NAME, "time").get_attribute('datetime')
                    tweet_data['created_at'] = date_and_time
                except NoSuchElementException:
                    pass
                try:
                    counts = article.find_element(By.CSS_SELECTOR, COUNT_CSS)
                    label = counts.get_attribute('aria-label').split(", ")
                    count_data = {'replies': 0,
                                  'Retweets': 0,
                                  'likes': 0,
                                  'views': 0}
                    for item in label:
                        try:
                            item_split = item.split(" ")
                            count_data[item_split[1]] = int(item_split[0])
                        except ValueError as ve:
                            logging.error(
                                f"Unable to convert count to integer: {ve}")
                        except Exception as e:
                            logging.error(
                                f"An unknown error occurred when parsing counts: {e}")

                    tweet_data['like_count'] = count_data['likes']
                    tweet_data['reply_count'] = count_data['replies']
                    tweet_data['retweet_count'] = count_data['Retweets']
                    tweet_data['views_count'] = count_data['views']
                except NoSuchElementException:
                    pass

                tweets_data.append(tweet_data)
        except NoSuchElementException as e:
            logging.error(f"Error occurred while finding articles: {e}")

        logging.info(
            f"Number of tweets received this time: {len(tweets_data)}")
        return tweets_data

    def scroll_and_scrap(self):
        """Scrolls through the page and scraps tweets."""
        tweets_list = []
        ROUND = 0
        SCROLL_PAUSE_TIME = random.uniform(3, 7)
        try:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            while True:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

                tweets_list += self.scrap_tweets()
                ROUND += 1
                logging.info(
                    f'Round {ROUND} complete. Please wait, scraping...')

            self.df = pd.DataFrame(tweets_list)
            logging.info('Scraping Completed')
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            if tweets_list is not None:
                self.df = pd.DataFrame(tweets_list)
                logging.error(f"Saved data till now.")
        finally:
            if self.driver is not None:
                self.driver.quit()
        return self.df if hasattr(self, 'df') else None
