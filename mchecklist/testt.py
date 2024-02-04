from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

options = Options()
user_agent = UserAgent().random
options.add_argument(f"--user-agent={user_agent}")
# options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

driver.get("https://rateyourmusic.com/artist/viper-1")

expand_buttons = driver.find_elements(By.CLASS_NAME, 'disco_expand_section_btn')
showing_amounts = driver.find_element(By.ID, 'discography').find_elements(By.CLASS_NAME, "disco_header_top")
cookies_button = driver.find_element(By.CLASS_NAME, "fc-cta-consent")

cookies_button.click()

highest = 0
for i in range(0,3):
    showing_amount = showing_amounts[i].find_element(By.CLASS_NAME, 'disco_showing').find_element(By.CSS_SELECTOR, "span").text
    release_amount = int(showing_amount[showing_amount.rfind(" ") + 1:])
    if release_amount > highest:
        highest = release_amount
    print(release_amount)
    
    driver.execute_script("arguments[0].click();", expand_buttons[i])

# Should wait the proper amount of time for releases to load
time.sleep(highest/40)
src = driver.page_source
driver.quit()

soup = BeautifulSoup(src, "html.parser")

releases_dict = {}

for id_ in ["s", "e", "m"]:
    releases = soup.select(f"#disco_type_{id_} .disco_release")

    for release in releases:
        title_and_link = release.select_one(".disco_info a")
        title = title_and_link["title"]
        link = title_and_link["href"]

        average_check = release.select_one(".disco_avg_rating").contents
        # If the average value exists (aka, if the release has any ratings)
        if len(average_check) > 0:
            average = average_check[0]
        else:
            continue

        ratings = release.select_one(".disco_ratings").contents[0]

        year_check = (
            release.select_one(".disco_subline").select_one("span").contents
        )
        # If the release has a listed year
        if len(year_check) > 0:
            year = year_check[0]
        else:
            year = "N/A"

        print({
            "Link": link,
            "Average": average,
            "Ratings": ratings,
            "Year": year,
        })
