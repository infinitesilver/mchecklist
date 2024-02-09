from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from typing import Dict, Optional
from collections import namedtuple


ArtistReleases = namedtuple('ArtistReleases', ['artist_name', 'releases'])


def get_releases(artist: str, release_types=["album"]) -> ArtistReleases:
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

    for type in release_types:
        match (type):
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
            title_and_link = release.select_one(".disco_info a")
            title = title_and_link["title"]
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

            releases_list.append(
                {
                    "Title": title,
                    "Link": link,
                    "Average": average,
                    "Ratings": ratings,
                    "Year": year,
                }
            )

    return ArtistReleases(artist_name, releases_list)


def get_one_release(artist, release_title) -> ArtistReleases:
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

    for id_ in ["s", "e", "m"]:
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
                "Title": title,
                "Link": link,
                "Average": average,
                "Ratings": ratings,
                "Year": year,
            }


def rymify(artist_name: str) -> str:
    """Converts an artist or release name to how it would appear in an RYM link."""

    # Convert to lowercase, convert ampersand to "and", and replace spaces with dashes
    return artist_name.lower().replace(" & ", "-and-").replace(" ", "-")


# Debug
if __name__ == "__main__":
    print(get_releases("Classic J", ["album", "ep"]))
