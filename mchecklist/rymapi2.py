from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
from fake_useragent import UserAgent
from typing import Dict
import re


def get_releases(artist: str, release_type="album") -> Dict:
    match (release_type):
        case ("album"):
            id_ = "s"
        case ("ep"):
            id_ = "e"
        case ("mixtape"):
            id_ = "m"
        case _:
            raise ValueError("Not a valid release type")

    headers = {"User-Agent": UserAgent().random}
    response = requests.get(
        f"https://rateyourmusic.com/artist/{rymify(artist)}", headers=headers
    )

    print(f"https://rateyourmusic.com/artist/{rymify(artist)}")
    soup = BeautifulSoup(response.content, "html.parser")

    releases = soup.select(f"#disco_type_{id_} .disco_release")
    print(soup.select_one("#disco_header_e"))
    releases_dict = {}

    for release in releases:
        title_and_link = release.select_one(".disco_info a")
        title = title_and_link["title"]
        link = title_and_link["href"]
        average = release.select_one(".disco_avg_rating").contents[0]
        ratings = release.select_one(".disco_ratings").contents[0]
        year = release.select_one(".disco_subline").select_one("span").contents[0]
        releases_dict[title] = {
            "Link": link,
            "Average": average,
            "Ratings": ratings,
            "Year": year,
        }
        print(releases_dict[title])


def rymify(artist_name: str) -> str:
    """Converts an artist or release name to how it would appear in an RYM link."""

    # Step 1: Convert to lowercase, replace spaces with dashes, and convert ampersand to "and"
    step1 = unidecode(artist_name.lower()).replace(" ", "-").replace(" & ", "-and-")

    # Step 2: Remove non-alphanumeric characters
    step2 = re.sub("[^0-9a-zA-Z]+", "_", step1)

    return step2


# Debug
get_releases("xtc 2", "ep")
