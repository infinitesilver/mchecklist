from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from unidecode import unidecode
from fake_useragent import UserAgent
from typing import Dict
import re


class RymApi:
    def __init__(self):
        options = Options()
        user_agent = UserAgent().random
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.page_counter = 0

    def reset_driver(self, current_link):
        self.driver.quit()

        options = Options()
        user_agent = UserAgent().random
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

        self.driver.get(current_link)
        self.page_counter = 0

    def quit(self):
        self.driver.quit()

    def get_artist(self, artist):
        pass

    def get_release(self, artist, release_name) -> (str, Dict):
        pass

    def get_releases(self, artist, release_type="album") -> Dict:
        if release_type == "album":
            id_ = "s"
        elif release_type == "mixtape":
            id_ = "m"
        elif release_type == "ep":
            id_ = "e"
        else:
            raise ValueError("Not a valid release type")

        table = self.driver.find_element(By.ID, "disco_type_" + id_)
        releases = table.find_elements(By.CLASS_NAME, "disco_release")

        releases_dict = {}

        for release in releases:
            title_and_link = release.find_element(
                By.CLASS_NAME, "disco_mainline"
            ).find_element(By.TAG_NAME, "a")
            title = title_and_link.accessible_name
            link = title_and_link.get_attribute("href")

            year = release.find_element(By.CLASS_NAME, "disco_subline").text[:4]
            ratings = release.find_element(By.CLASS_NAME, "disco_ratings").text
            average = release.find_element(By.CLASS_NAME, "disco_avg_rating").text

            # Debug
            print(title, link, year, ratings, average)

            release_info = {
                "Link": link,
                "Release Year": year,
                "Ratings": ratings,
                "Score": average,
            }

            releases_dict[title] = release_info

        return releases_dict

    def rymify(string: str):
        """Converts an artist or release name to how it would appear in an RYM link."""

        # Step 1: Convert to lowercase, replace spaces with dashes, and convert ampersand to "and"
        step1 = unidecode(string.lower()).replace(" ", "-").replace(" & ", "-and-")

        # Step 2: Remove non-alphanumeric characters
        step2 = re.sub("[^0-9a-zA-Z]+", "_", step1)

        return step2
