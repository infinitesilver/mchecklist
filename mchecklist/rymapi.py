from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from typing import List, Dict, Optional


def _get_release_info(
    release_type: str, artist_name: str, release: BeautifulSoup.Tag
) -> Optional[Dict]:
    title_and_link = release.select_one(".disco_info a")
    title = title_and_link["title"]
    link = title_and_link["href"]

    ratings_check = release.select_one(".disco_ratings").contents
    # If the ratings value exists (aka, if the release has any ratings)
    if len(ratings_check) > 0:
        ratings = ratings_check[0]
    else:
        return

    average = release.select_one(".disco_avg_rating").contents[0]

    year_check = release.select_one(".disco_subline").select_one("span").contents
    # If the release has a listed year
    if len(year_check) > 0:
        year = year_check[0]
    else:
        year = "N/A"

    return {
        "Artist": artist_name,
        "Title": title,
        "Link": link,
        "Average": average,
        "Ratings": ratings,
        "Year": year,
        "Type": release_type,
    }


def get_releases(artist: str, release_types=["album"]) -> List:
    """Get all releases of a certain type or types"""

    headers = {"User-Agent": UserAgent().random}
    response = requests.get(
        f"https://rateyourmusic.com/artist/{rymify(artist)}", headers=headers
    )

    # Immediately terminate if artist doesn't exist
    if not response.status_code == 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    releases_list = []

    artist_name = soup.select_one(".artist_page meta")["content"]

    for release_type in release_types:
        match (release_type):
            case ("album"):
                id_ = "s"
            case ("ep"):
                id_ = "e"
            case ("mixtape"):
                id_ = "m"
            case _:
                raise ValueError("Not a valid release type")

        releases = soup.select(f"#disco_type_{id_} .disco_release")

        for release in releases:
            releases_list.append(_get_release_info(type, artist_name, release))

    return releases_list


def get_one_release(artist, release_title) -> List:
    """Get the release that matches the title"""

    headers = {"User-Agent": UserAgent().random}
    response = requests.get(
        f"https://rateyourmusic.com/artist/{rymify(artist)}", headers=headers
    )
    # Immediately terminate if artist doesn't exist
    if not response.status_code == 200:
        return

    soup = BeautifulSoup(response.content, "html.parser")

    releases_dict = {}

    for type in ["album", "ep", "mixtape"]:
        match (type):
            case ("album"):
                id_ = "s"
            case ("ep"):
                id_ = "e"
            case ("mixtape"):
                id_ = "m"

        releases = soup.select(f"#disco_type_{id_} .disco_release")

        for release in releases:
            title_and_link = release.select_one(".disco_info a")
            title = title_and_link["title"]

            if not title == release_title:
                continue

            link = title_and_link["href"]

            ratings_check = release.select_one(".disco_ratings").contents
            # If the ratings value exists (aka, if the release has any ratings)
            if len(ratings_check) > 0:
                ratings = ratings_check[0]
            else:
                continue

            average = release.select_one(".disco_avg_rating").contents[0]

            year_check = (
                release.select_one(".disco_subline").select_one("span").contents
            )
            # If the release has a listed year
            if len(year_check) > 0:
                year = year_check[0]
            else:
                year = "N/A"

            return {
                "Artist": artist,
                "Title": title,
                "Link": link,
                "Average": average,
                "Ratings": ratings,
                "Year": year,
                "Type": type,
            }


def rymify(artist_name: str) -> str:
    """Converts an artist or release name to how it would appear in an RYM link."""

    # Convert to lowercase, convert ampersand to "and", and replace spaces with dashes
    return artist_name.lower().replace(" & ", "-and-").replace(" ", "-")


# Debug
if __name__ == "__main__":
    print(get_releases("Classic J", ["album", "ep"]))
